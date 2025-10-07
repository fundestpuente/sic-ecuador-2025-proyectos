"""Prepara DataFrames reales para las visualizaciones en `charts.py`.

Genera y guarda:
- df_mapa_calor: filas por (region, fecha) con columna 'consumo' (MWh)
- df_antes, df_durante, df_despues: series temporales agregadas por mes con columnas 'fecha' y 'consumo'
- df_facturacion: tabla por región con columna 'impacto_economico' (USD)

Uso recomendado desde la carpeta `Proyecto/src`:
    python -m visualization.prepare_charts_data

El script intenta usar `DataLoader` del paquete `data_processing`. Si no puede importarlo
ajusta `sys.path` para permitir ejecución directa.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
import pandas as pd

# Import DataLoader robustamente (soporta ejecución como módulo o como script)
try:
    from ..data_processing.data_loader import DataLoader
except Exception:
    # Ejecutando directamente desde src/visualization -> ajustar sys.path
    this_dir = os.path.dirname(__file__)
    src_dir = os.path.abspath(os.path.join(this_dir, '..'))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    try:
        from data_processing.data_loader import DataLoader
    except Exception as e:
        raise ImportError("No se pudo importar DataLoader desde data_processing: " + str(e))


def prepare_charts_data(base_path: str | None = None, save_exports: bool = True) -> dict:
    """Carga datos reales y construye los DataFrames usados por `charts.py`.

    Args:
        base_path: ruta relativa a `Proyecto` o absoluta hacia la carpeta `data/raw`. Si None usa default.
        save_exports: si True guarda CSVs en data/exports/charts.

    Returns:
        Diccionario con los DataFrames: df_mapa_calor, df_antes, df_durante, df_despues, df_facturacion
    """
    loader = DataLoader(base_path=base_path) if base_path is not None else DataLoader()

    df_fact = loader.load_facturacion_data()
    if df_fact is None:
        raise RuntimeError(f"No se pudo cargar facturación desde: {loader.facturacion_path}")

    # --- Preparar df_mapa_calor ---
    # Detectar columnas de consumo por región (prefijo 'MWh_')
    mwh_cols = [c for c in df_fact.columns if c.startswith('MWh_')]
    if not mwh_cols:
        raise RuntimeError("No se encontraron columnas 'MWh_' en facturación. Revisa los archivos de entrada.")

    # Crear columna fecha a partir de año/mes del archivo si existe
    if 'año_archivo' in df_fact.columns and 'mes_archivo' in df_fact.columns:
        # Coercionar a numérico y construir fecha sólo donde ambos valores existan
        year_num = pd.to_numeric(df_fact['año_archivo'], errors='coerce')
        month_num = pd.to_numeric(df_fact['mes_archivo'], errors='coerce')
        df_fact['fecha'] = pd.NaT
        valid_mask = year_num.notna() & month_num.notna()
        if valid_mask.any():
            # Construir fechas sólo para filas válidas
            year_str = year_num[valid_mask].astype(int).astype(str)
            month_str = month_num[valid_mask].astype(int).astype(str).str.zfill(2)
            date_str = year_str + '-' + month_str + '-01'
            df_fact.loc[valid_mask, 'fecha'] = pd.to_datetime(date_str, errors='coerce')
    else:
        # Si no hay año/mes, intentar columna 'fecha' existente
        if 'fecha' in df_fact.columns:
            df_fact['fecha'] = pd.to_datetime(df_fact['fecha'], errors='coerce')
        else:
            # Fallback: establecer fecha a NaT
            df_fact['fecha'] = pd.NaT

    # Melt las columnas MWh_* para tener (region, fecha, consumo)
    df_melt = df_fact.melt(id_vars=[c for c in df_fact.columns if c not in mwh_cols], value_vars=mwh_cols, var_name='mwh_col', value_name='consumo')
    # Extraer código de región de 'MWh_BOL' -> 'BOL'
    df_melt['region'] = df_melt['mwh_col'].str.replace('MWh_', '', regex=False)
    df_mapa_calor = df_melt[['region', 'fecha', 'consumo']].copy()

    # Eliminar filas sin fecha o sin consumo
    df_mapa_calor = df_mapa_calor.dropna(subset=['fecha', 'consumo'])

    # --- Preparar series temporales agregadas ---
    # Agregar consumo total (sum sobre regiones) por fecha (mes)
    df_mes = df_mapa_calor.groupby('fecha', dropna=True)['consumo'].sum().reset_index()
    df_mes = df_mes.sort_values('fecha')

    # Definir periodos: antes (<2024-09-01), durante (2024-09-01..2024-12-31), despues (>=2025-01-01)
    periodo_inicio = datetime(2024, 9, 1)
    periodo_fin = datetime(2024, 12, 31)

    df_antes = df_mes[df_mes['fecha'] < periodo_inicio].rename(columns={'consumo': 'consumo'})
    df_durante = df_mes[(df_mes['fecha'] >= periodo_inicio) & (df_mes['fecha'] <= periodo_fin)].rename(columns={'consumo': 'consumo'})
    df_despues = df_mes[df_mes['fecha'] >= datetime(2025, 1, 1)].rename(columns={'consumo': 'consumo'})

    # Asegurar columnas esperadas por charts.py: fecha, consumo
    for df in (df_antes, df_durante, df_despues):
        if 'fecha' not in df.columns:
            df['fecha'] = pd.NaT
        if 'consumo' not in df.columns:
            df['consumo'] = 0

    # --- Preparar df_facturacion para impacto económico por región ---
    fact_cols = [c for c in df_fact.columns if c.startswith('FACT_')]
    if not fact_cols:
        raise RuntimeError("No se encontraron columnas 'FACT_' en facturación. Revisa los archivos de entrada.")

    # Agregar impacto por región (sum de FACT_{REG})
    impact_rows = []
    for col in fact_cols:
        region = col.replace('FACT_', '')
        total = pd.to_numeric(df_fact[col], errors='coerce').sum()
        impact_rows.append({'region': region, 'impacto_economico': float(total if pd.notna(total) else 0.0)})

    df_facturacion_out = pd.DataFrame(impact_rows).sort_values('impacto_economico', ascending=False).reset_index(drop=True)

    # Guardar resultados opcionalmente
    exports = {}
    if save_exports:
        exports_dir = os.path.join(loader.project_root, 'data', 'exports', 'charts')
        os.makedirs(exports_dir, exist_ok=True)
        df_mapa_calor.to_csv(os.path.join(exports_dir, 'df_mapa_calor.csv'), index=False)
        df_antes.to_csv(os.path.join(exports_dir, 'df_antes.csv'), index=False)
        df_durante.to_csv(os.path.join(exports_dir, 'df_durante.csv'), index=False)
        df_despues.to_csv(os.path.join(exports_dir, 'df_despues.csv'), index=False)
        df_facturacion_out.to_csv(os.path.join(exports_dir, 'df_facturacion_impacto.csv'), index=False)
        exports['path'] = exports_dir

    outputs = {
        'df_mapa_calor': df_mapa_calor,
        'df_antes': df_antes,
        'df_durante': df_durante,
        'df_despues': df_despues,
        'df_facturacion': df_facturacion_out,
        'exports': exports
    }

    # Mostrar resumen
    print(f"[OK] Preparados DataFrames para charts. Filas mapa_calor: {len(df_mapa_calor)}, meses totales: {len(df_mes)}")
    print("Periodos: antes=", df_antes['fecha'].min(), "->", df_antes['fecha'].max())
    print("         durante=", df_durante['fecha'].min(), "->", df_durante['fecha'].max())
    print("         despues=", df_despues['fecha'].min(), "->", df_despues['fecha'].max())

    return outputs


if __name__ == '__main__':
    # Ejecutar y exportar CSVs
    try:
        out = prepare_charts_data()
        print('\nArchivos exportados en:', out.get('exports', {}).get('path'))
    except Exception as e:
        print('[ERROR] No se pudieron preparar los DataFrames:', e)

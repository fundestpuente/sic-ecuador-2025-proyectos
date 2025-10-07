"""
Dashboard interactivo.

Este script usa Streamlit + Plotly para mostrar:
 - Heatmap de horas críticas durante cortes programados (por región y hora)
 - Comparación temporal: antes / durante / después
 - Impacto económico por región (barras)
 - Demanda eléctrica agregada antes/durante/después
 - Correlaciones simples entre cortes y facturación

Uso:
    cd Proyecto/src
    streamlit run visualization/integrated_dashboard.py

Notas:
 - Requiere instalar streamlit y plotly: pip install streamlit plotly
 - El dashboard intentará cargar los CSVs de `data/exports/charts` generados por `prepare_charts_data.py`.
   Si faltan, generará los DataFrames usando `prepare_charts_data` y `DataLoader`.
"""

from __future__ import annotations

import os
import sys
from typing import Optional

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import unicodedata

# Import helper to prepare data; allow running from src/visualization directly
try:
    from visualization.prepare_charts_data import prepare_charts_data
except Exception:
    this_dir = os.path.dirname(__file__)
    src_dir = os.path.abspath(os.path.join(this_dir, '..'))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    from prepare_charts_data import prepare_charts_data

# Import DataLoader for cortes/balance if needed
try:
    from data_processing.data_loader import DataLoader
except Exception:
    # adjust path and retry
    this_dir = os.path.dirname(__file__)
    src_dir = os.path.abspath(os.path.join(this_dir, '..'))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    from data_processing.data_loader import DataLoader


def load_or_prepare(exports_dir: Optional[str] = None):
    """Carga los CSVs preparados si existen, si no, genera los DataFrames y los guarda.

    Devuelve diccionario con los DataFrames necesarios.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    default_exports = os.path.join(project_root, 'data', 'exports', 'charts')
    exports_dir = exports_dir or default_exports

    paths = {
        'df_mapa_calor': os.path.join(exports_dir, 'df_mapa_calor.csv'),
        'df_antes': os.path.join(exports_dir, 'df_antes.csv'),
        'df_durante': os.path.join(exports_dir, 'df_durante.csv'),
        'df_despues': os.path.join(exports_dir, 'df_despues.csv'),
        'df_facturacion': os.path.join(exports_dir, 'df_facturacion_impacto.csv')
    }

    missing = [k for k, p in paths.items() if not os.path.exists(p)]
    if missing:
        st.info('Generando DataFrames a partir de los datos reales (prepare_charts_data)...')
        outs = prepare_charts_data(save_exports=True)
        # ensure CSVs exist now
    # Cargar desde CSVs (siempre usar parse_dates donde aplique)
    df_mapa_calor = pd.read_csv(paths['df_mapa_calor'], parse_dates=['fecha'])
    df_antes = pd.read_csv(paths['df_antes'], parse_dates=['fecha'])
    df_durante = pd.read_csv(paths['df_durante'], parse_dates=['fecha'])
    df_despues = pd.read_csv(paths['df_despues'], parse_dates=['fecha'])
    df_facturacion = pd.read_csv(paths['df_facturacion'])

    return {
        'df_mapa_calor': df_mapa_calor,
        'df_antes': df_antes,
        'df_durante': df_durante,
        'df_despues': df_despues,
        'df_facturacion': df_facturacion
    }


def heatmap_critical_hours(cortes_df: pd.DataFrame, region_col: str = 'unidad_de_negocio') -> pd.DataFrame:
    """Construye pivot table region x hora (0-23) con conteo de cortes."""
    df = cortes_df.copy()
    # Normalizar nombres
    if 'hora_inicio' in df.columns:
        # extraer hora como entero
        df['hora_inicio'] = df['hora_inicio'].astype(str)
        df['hora'] = df['hora_inicio'].str.split(':').str[0].astype(float).fillna(0).astype(int)
    else:
        df['hora'] = 0

    if region_col not in df.columns:
        df[region_col] = 'UNKNOWN'

    pivot = df.groupby([region_col, 'hora']).size().reset_index(name='count')
    heat = pivot.pivot(index=region_col, columns='hora', values='count').fillna(0)
    # Ensure hours 0..23 present
    for h in range(24):
        if h not in heat.columns:
            heat[h] = 0
    heat = heat.reindex(sorted(heat.columns), axis=1)
    return heat


def main():
    st.set_page_config(layout='wide', page_title='Dashboard Demanda Eléctrica')
    st.title('Dashboard: Demanda eléctrica y efectos de cortes (antes / durante / después)')

    # Cargar datos preparados
    data = load_or_prepare()
    df_mapa_calor = data['df_mapa_calor']
    df_antes = data['df_antes']
    df_durante = data['df_durante']
    df_despues = data['df_despues']
    df_facturacion = data['df_facturacion']

    # Cargar cortes reales para heatmap de horas (usar DataLoader directly)
    loader = DataLoader()
    cortes = loader.load_cortes_data()
    if cortes is None:
        st.warning('No se encontraron datos de cortes; las horas críticas estarán vacías')
        cortes = pd.DataFrame(columns=['unidad_de_negocio', 'hora_inicio'])

    # Sidebar controls
    st.sidebar.header('Filtros')
    regiones = sorted(df_mapa_calor['region'].unique()) if not df_mapa_calor.empty else []
    selected_regions = st.sidebar.multiselect('Seleccionar regiones', regiones, default=regiones[:6])

    st.sidebar.markdown('---')
    # Selector de periodo (aplica a series y heatmap)
    period_options = ['Todos', 'Antes', 'Durante', 'Después']
    period_select = st.sidebar.selectbox('Periodo preseleccionado', period_options, index=0)

    # Date range filter for time series (override period if set)
    min_date = df_mapa_calor['fecha'].min() if not df_mapa_calor.empty else None
    max_date = df_mapa_calor['fecha'].max() if not df_mapa_calor.empty else None
    date_range = st.sidebar.date_input('Rango de fechas (series) — opcional', [min_date, max_date]) if min_date is not None else None

    st.sidebar.markdown('---')
    # Normalización por región
    normalization = st.sidebar.selectbox('Normalización', ['Ninguna', 'Por región (max=1)', 'Per cápita (si disponible)'])

    # Escala logarítmica para ejes Y
    log_scale = st.sidebar.checkbox('Escala logarítmica (Y) en series y demanda', value=False)

    st.sidebar.markdown('---')

    # Layout: two columns top, one row bottom
    col1, col2 = st.columns([1, 1])

    # Heatmap horas criticas
    with col1:
        st.subheader('Horas críticas durante cortes (conteo por hora y región)')
        heat = heatmap_critical_hours(cortes)
        # Aplicar filtro de periodo: si el usuario seleccionó un periodo, filtrar cortes
        heat_filtered = heat.copy()
        if period_select != 'Todos' and not cortes.empty:
            # filtrar cortes en memoria según periodo
            if period_select == 'Antes':
                mask = cortes['fecha_inicio'] < pd.to_datetime('2024-09-01')
            elif period_select == 'Durante':
                mask = (cortes['fecha_inicio'] >= pd.to_datetime('2024-09-01')) & (cortes['fecha_inicio'] <= pd.to_datetime('2024-12-31'))
            else:  # Después
                mask = cortes['fecha_inicio'] >= pd.to_datetime('2025-01-01')
            cortes_period = cortes[mask]
            heat_filtered = heatmap_critical_hours(cortes_period)

        if selected_regions:
            heat_plot = heat_filtered.loc[heat_filtered.index.isin(selected_regions)] if not heat_filtered.empty else heat_filtered
        else:
            heat_plot = heat_filtered

        if heat_plot.empty:
            st.write('No hay datos para mostrar')
        else:
            # Normalización por región (cada fila 0-1)
            heat_display = heat_plot.copy()
            if normalization == 'Por región (max=1)':
                heat_display = heat_display.div(heat_display.max(axis=1).replace(0, 1), axis=0)

            fig = px.imshow(heat_display.values, x=heat_display.columns.astype(str), y=heat_display.index, labels={'x': 'Hora', 'y': 'Región', 'color': 'Cortes'}, aspect='auto', color_continuous_scale='YlOrRd')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    # Series comparativa antes/durante/despues
    with col2:
        st.subheader('Comparación Antes / Durante / Después (consumo mensual)')
        # Concatenate series with label
        def prepare_series(df, label):
            out = df.copy()
            out = out.sort_values('fecha')
            out = out[['fecha', 'consumo']]
            out['periodo'] = label
            return out

        s_antes = prepare_series(df_antes, 'Antes')
        s_durante = prepare_series(df_durante, 'Durante')
        s_despues = prepare_series(df_despues, 'Después')
        all_s = pd.concat([s_antes, s_durante, s_despues], ignore_index=True)

        if period_select != 'Todos':
            if period_select == 'Antes':
                all_s = all_s[all_s['periodo'] == 'Antes']
            elif period_select == 'Durante':
                all_s = all_s[all_s['periodo'] == 'Durante']
            else:
                all_s = all_s[all_s['periodo'] == 'Después']

        if date_range and len(date_range) == 2 and date_range[0] is not None:
            start_dt, end_dt = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            all_s = all_s[(all_s['fecha'] >= start_dt) & (all_s['fecha'] <= end_dt)]

        if all_s.empty:
            st.write('No hay datos de series para el rango seleccionado')
        else:
            # Aplicar normalización si corresponde
            plot_df = all_s.copy()
            if normalization == 'Por región (max=1)':
                # Normalizar por período máximo (escala 0-1)
                plot_df['consumo'] = plot_df.groupby('periodo')['consumo'].transform(lambda s: s / (s.max() if s.max() > 0 else 1))
            elif normalization == 'Per cápita (si disponible)':
                # No tenemos clientes en estas series; se deja como fallback
                pass

            fig2 = px.line(plot_df, x='fecha', y='consumo', color='periodo', markers=True)
            if log_scale:
                fig2.update_yaxes(type='log')
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)

    # Second row: economic impact and demand
    st.markdown('---')
    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader('Impacto económico por región')
        if df_facturacion.empty:
            st.write('No hay datos de facturación')
        else:
            fact_df = df_facturacion.copy()
            if normalization == 'Por región (max=1)':
                fact_df['impacto_economico'] = fact_df['impacto_economico'] / fact_df['impacto_economico'].max()

            fig3 = px.bar(fact_df, x='region', y='impacto_economico', color='region', title='Impacto económico (USD)')
            if log_scale:
                fig3.update_yaxes(type='log')
            fig3.update_layout(showlegend=False, height=450)
            st.plotly_chart(fig3, use_container_width=True)

    with c2:
        st.subheader('Demanda eléctrica (proxy por facturación MWh)')
        # Intentar usar balance data, si no está, usar df_mapa_calor agregada
        balance = loader.load_balance_data()
        if balance is not None and 'generacion_total_mwh' in balance.columns:
            bal = balance.copy()
            # intentar usar fecha_archivo
            if 'fecha_archivo' in bal.columns:
                bal['fecha_archivo'] = pd.to_datetime(bal['fecha_archivo'], errors='coerce')
                balm = bal.groupby(pd.Grouper(key='fecha_archivo', freq='M')).sum().reset_index()
                fig4 = go.Figure()
                if 'generacion_total_mwh' in balm.columns:
                    y = balm['generacion_total_mwh'].copy()
                    if normalization == 'Por región (max=1)':
                        y = y / (y.max() if y.max() > 0 else 1)
                    fig4.add_trace(go.Scatter(x=balm['fecha_archivo'], y=y, name='Generación (MWh)'))
                if 'demanda_total_mwh' in balm.columns:
                    y2 = balm['demanda_total_mwh'].copy()
                    if normalization == 'Por región (max=1)':
                        y2 = y2 / (y2.max() if y2.max() > 0 else 1)
                    fig4.add_trace(go.Scatter(x=balm['fecha_archivo'], y=y2, name='Demanda (MWh)'))
                fig4.update_layout(height=450)
                if log_scale:
                    fig4.update_yaxes(type='log')
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.write('Balance cargado pero no tiene columna fecha_archivo para agrupar')
        else:
            # usar df_mapa_calor como proxy agregada por mes
            proxy = df_mapa_calor.copy()
            proxy['mes'] = proxy['fecha'].dt.to_period('M').dt.to_timestamp()
            proxym = proxy.groupby('mes')['consumo'].sum().reset_index()
            if period_select != 'Todos':
                if period_select == 'Antes':
                    proxym = proxym[proxym['mes'] < pd.to_datetime('2024-09-01')]
                elif period_select == 'Durante':
                    proxym = proxym[(proxym['mes'] >= pd.to_datetime('2024-09-01')) & (proxym['mes'] <= pd.to_datetime('2024-12-31'))]
                else:
                    proxym = proxym[proxym['mes'] >= pd.to_datetime('2025-01-01')]

            y = proxym['consumo'].copy()
            if normalization == 'Por región (max=1)':
                y = y / (y.max() if y.max() > 0 else 1)

            fig4 = px.line(proxym.assign(consumo=y), x='mes', y='consumo', title='Consumo agregado mensual (proxy)')
            if log_scale:
                fig4.update_yaxes(type='log')
            fig4.update_layout(height=450)
            st.plotly_chart(fig4, use_container_width=True)

    st.markdown('---')
    st.subheader('Correlaciones y análisis sencillo')
    # Correlación: número de cortes por región vs impacto económico
    # Construir conteo de cortes por unidad_de_negocio
    cortes_counts = cortes['unidad_de_negocio'].value_counts().rename_axis('region').reset_index(name='cortes') if not cortes.empty else pd.DataFrame(columns=['region', 'cortes'])

    # Normalización de textos (quita acentos, pasa a mayúsculas y limpia espacios)
    def normalize_str(s: object) -> str:
        if pd.isna(s):
            return ''
        t = str(s).upper().strip()
        # Quitar acentos
        t = unicodedata.normalize('NFKD', t)
        t = ''.join(ch for ch in t if not unicodedata.combining(ch))
        # Reemplazar varios separadores problemáticos
        for bad in ['/', '-', '_', ',', '.']:
            t = t.replace(bad, ' ')
        # Colapsar espacios
        t = ' '.join(t.split())
        return t

    # Limpiar df_facturacion y eliminar filas obviamente malformadas
    eco = df_facturacion.copy()
    # eliminar filas cuya columna 'region' tenga demasiadas comas o caracteres no esperados
    eco['region'] = eco['region'].astype(str).str.strip()
    eco = eco[~eco['region'].str.contains(',')].copy()

    # Mapeo manual (heurístico) desde códigos en facturación a nombres de regiones usados en cortes
    # Puedes ajustar este diccionario si tus códigos son distintos
    code_to_region = {
        'GYE': 'GUAYAQUIL',
        'GLR': 'GUAYAS LOS RIOS',
        'MAN': 'MANABI',
        'EOR': 'EL ORO',
        'MLG': 'MILAGRO',
        'STD': 'SANTO DOMINGO',
        'SUC': 'SUCUMBIOS',
        'STE': 'SANTA ELENA',
        'ESM': 'ESMERALDAS',
        'LRS': 'LOS RIOS',
        'BOL': 'BOLIVAR'
    }

    # Crear columna de coincidencia normalizada en ambos DataFrames
    cortes_counts['region_norm'] = cortes_counts['region'].apply(normalize_str)
    # Para facturación, convertir códigos como 'GYE' a nombres si existen en el mapeo, sino usar el mismo código
    eco['region_mapped'] = eco['region'].apply(lambda r: code_to_region.get(r, r))
    eco['region_norm'] = eco['region_mapped'].apply(normalize_str)

    # Merge usando las columnas normalizadas
    corr_df = pd.merge(cortes_counts, eco, left_on='region_norm', right_on='region_norm', how='inner')

    if corr_df.empty:
        # Mostrar pistas de depuración para ayudar al usuario a crear un mapeo correcto
        st.write('No hay suficientes datos para correlación (no se encontraron regiones coincidentes).')
        st.markdown('Regiones (cortes) — ejemplos:')
        st.write(list(cortes_counts['region'].unique())[:20])
        st.markdown('Regiones (facturación) — ejemplos:')
        st.write(list(df_facturacion['region'].unique())[:20])
        st.markdown('Sugerencia: añade o ajusta entradas en `code_to_region` para mapear los códigos de facturación a los nombres de `unidad_de_negocio`.')
    else:
        # Seleccionar campos útiles para graficar
        plot_df = corr_df.copy()
        # Si hay múltiples filas por región (p. ej. diferentes archivos), agregar
        plot_df = plot_df.groupby(['region_x', 'region_norm'], as_index=False).agg({'cortes': 'sum', 'impacto_economico': 'sum'})
        plot_df = plot_df.rename(columns={'region_x': 'region'})
        fig5 = px.scatter(plot_df, x='cortes', y='impacto_economico', text='region', size='impacto_economico')
        fig5.update_traces(textposition='top center')
        st.plotly_chart(fig5, use_container_width=True)


if __name__ == '__main__':
    main()
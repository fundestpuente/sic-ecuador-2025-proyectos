"""
Visualizaciones avanzadas para análisis energético
Incluye: mapa de calor, series temporales comparativas, gráfico de impacto económico
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
try:
    # intentar import como paquete
    from visualization.prepare_charts_data import prepare_charts_data
except Exception:
    # fallback: ajustar sys.path para permitir ejecución directamente desde src/visualization
    import sys
    this_dir = os.path.dirname(__file__)
    src_dir = os.path.abspath(os.path.join(this_dir, '..'))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    from prepare_charts_data import prepare_charts_data

# Cargar datos al importar el módulo (puedes cambiar save_exports=True para crear CSVs)
outs = prepare_charts_data(save_exports=False)
df_mapa_calor = outs['df_mapa_calor']
df_antes = outs['df_antes']
df_durante = outs['df_durante']
df_despues = outs['df_despues']
df_facturacion = outs['df_facturacion']

def crear_mapa_calor_consumo(datos, region_col='region', tiempo_col='fecha', consumo_col='consumo', save_path: str = None):
    """
    Mapa de calor: región vs tiempo vs consumo
    """
    # Trabajar con una copia
    df = datos.copy()

    # Asegurar que la columna de tiempo sea datetime; si es así, agrupar por mes para etiquetas más limpias
    try:
        df[tiempo_col] = pd.to_datetime(df[tiempo_col], errors='coerce')
    except Exception:
        # si no se puede convertir, dejar tal cual
        pass

    if pd.api.types.is_datetime64_any_dtype(df[tiempo_col]):
        # crear columna mensual (timestamp al primer día del mes) para ordenar correctamente
        df['_periodo_mes'] = df[tiempo_col].dt.to_period('M').dt.to_timestamp()
        col_time = '_periodo_mes'
    else:
        col_time = tiempo_col

    tabla = df.pivot_table(index=region_col, columns=col_time, values=consumo_col, aggfunc='sum')

    # Ordenar columnas cronológicamente si son datetimes
    try:
        cols_sorted = sorted(tabla.columns)
        tabla = tabla.reindex(columns=cols_sorted)
    except Exception:
        pass

    plt.figure(figsize=(12, 6))
    ax = sns.heatmap(tabla, cmap='YlGnBu', annot=False)
    plt.title('Mapa de calor de consumo energético')
    plt.xlabel('Fecha')
    plt.ylabel('Región')

    # Formatear etiquetas del eje x: usar YYYY-MM para mayor legibilidad
    xticks = tabla.columns
    labels = []
    for c in xticks:
        try:
            # si la columna es un Timestamp o Period
            if hasattr(c, 'strftime'):
                labels.append(c.strftime('%Y-%m'))
            else:
                ts = pd.to_datetime(c, errors='coerce')
                if pd.isna(ts):
                    labels.append(str(c))
                else:
                    labels.append(ts.strftime('%Y-%m'))
        except Exception:
            labels.append(str(c))

    ax.set_xticklabels(labels, rotation=45, ha='right')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        plt.close()
    else:
        plt.show()


def crear_serie_temporal_comparativa(antes, durante, despues, fecha_col='fecha', consumo_col='consumo', save_path: str = None):
    """
    Serie temporal comparando los 3 períodos
    """
    plt.figure(figsize=(14, 6))
    plt.plot(antes[fecha_col], antes[consumo_col], label='Antes de cortes')
    plt.plot(durante[fecha_col], durante[consumo_col], label='Durante cortes')
    plt.plot(despues[fecha_col], despues[consumo_col], label='Después de cortes')
    plt.title('Serie temporal de consumo energético')
    plt.xlabel('Fecha')
    plt.ylabel('Consumo (MWh)')
    plt.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        plt.close()
    else:
        plt.show()


def crear_grafico_impacto_economico(datos_facturacion, region_col='region', impacto_col='impacto_economico', save_path: str = None):
    """
    Impacto económico por región
    """
    resumen = datos_facturacion.groupby(region_col)[impacto_col].sum().sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    resumen.plot(kind='bar', color='tomato')
    plt.title('Impacto económico por región')
    plt.xlabel('Región')
    plt.ylabel('Impacto económico (USD)')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        plt.close()
    else:
        plt.show()

heatmap = crear_mapa_calor_consumo
serie_temporal = crear_serie_temporal_comparativa
grafico_impacto = crear_grafico_impacto_economico

# Visualizaciones avanzadas generadas exitosamente
print("Visualizaciones avanzadas generadas exitosamente")

# Asegúrate de que estos DataFrames estén definidos en tu entorno antes de ejecutar este script:
# df_mapa_calor, df_antes, df_durante, df_despues, df_facturacion

try:
    crear_mapa_calor_consumo(df_mapa_calor)
except Exception as e:
    print("[ERROR] No se pudo mostrar el mapa de calor:", e)

try:
    crear_serie_temporal_comparativa(df_antes, df_durante, df_despues)
except Exception as e:
    print("[ERROR] No se pudo mostrar la serie temporal:", e)

try:
    crear_grafico_impacto_economico(df_facturacion)
except Exception as e:
    print("[ERROR] No se pudo mostrar el gráfico de impacto económico:", e)


def run_and_save_all(export_dir: str | None = None, prefix: str = ''):
    """Genera todas las gráficas en orden y las guarda como PNGs en `export_dir`.

    Si export_dir es None, se usa `Proyecto/data/exports/charts/images`.
    """
    # Determinar project_root (subir dos niveles desde src/visualization -> Proyecto)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if export_dir is None:
        export_dir = os.path.join(project_root, 'data', 'exports', 'charts', 'images')

    os.makedirs(export_dir, exist_ok=True)

    # Nombres de archivo con timestamp
    ts = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    heatmap_path = os.path.join(export_dir, f"{prefix}heatmap_{ts}.png")
    serie_path = os.path.join(export_dir, f"{prefix}serie_temporal_{ts}.png")
    impacto_path = os.path.join(export_dir, f"{prefix}impacto_{ts}.png")

    print(f"Guardando imágenes en: {export_dir}")

    # Llamar a las funciones de plotting con save_path
    try:
        crear_mapa_calor_consumo(df_mapa_calor, save_path=heatmap_path)
        print(f"[OK] Heatmap guardado: {heatmap_path}")
    except Exception as e:
        print("[ERROR] al crear/guardar heatmap:", e)

    try:
        crear_serie_temporal_comparativa(df_antes, df_durante, df_despues, save_path=serie_path)
        print(f"[OK] Serie temporal guardada: {serie_path}")
    except Exception as e:
        print("[ERROR] al crear/guardar serie temporal:", e)

    try:
        crear_grafico_impacto_economico(df_facturacion, save_path=impacto_path)
        print(f"[OK] Gráfico impacto guardado: {impacto_path}")
    except Exception as e:
        print("[ERROR] al crear/guardar gráfico de impacto:", e)


if __name__ == '__main__':
    # Guardar todas las gráficas en exports
    run_and_save_all()
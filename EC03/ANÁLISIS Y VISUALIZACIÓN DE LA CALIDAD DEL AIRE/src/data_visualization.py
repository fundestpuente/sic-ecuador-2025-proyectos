"""
Módulo: Visualización de Datos de Calidad del Aire
---------------------------------------------------
Proporciona funciones para crear visualizaciones interactivas y estáticas
del análisis de calidad del aire, incluyendo series temporales, distribuciones,
correlaciones y análisis del Índice de Calidad del Aire (ICA).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Optional, Tuple
import warnings
import src.data_processing as dp

warnings.filterwarnings('ignore')

# Estilo de gráficos
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Paleta de colores ICA (según categorías internacionales)
ICA_COLORS = dp.get_ica_colors()
# Contaminantes principales
CONTAMINANTES = ['co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3']


def ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    """Garantiza que el índice sea datetime."""
    if not isinstance(df.index, pd.DatetimeIndex):
        if 'date' in df.columns:
            df = df.copy()
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
            df = df.set_index('date')
    return df


def plot_time_series(df: pd.DataFrame, columnas: List[str] = ['pm2_5', 'pm10'],figsize: Tuple[int, int] = (14, 6), titulo: str = "Evolución Temporal de Contaminantes", save_path: Optional[str] = None) -> None:
    """Gráfico de líneas para visualizar la evolución temporal de contaminantes.
    Parámetros:
        df: DataFrame con los datos (debe tener índice datetime).
        columnas: Lista de columnas a graficar.
        figsize: Tamaño de la figura.
        titulo: Título del gráfico.
        save_path: Ruta para guardar la imagen (si se proporciona).
    """
    df = ensure_datetime_index(df)
    fig, ax = plt.subplots(figsize=figsize)

    for col in columnas:
        if col in df.columns:
            ax.plot(df.index, df[col], label=col.upper(), linewidth=1.5, alpha=0.8)

    ax.set_xlabel("Fecha", fontsize=12)
    ax.set_ylabel("Concentración (µg/m³)", fontsize=12)
    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_ica_distribution(df: pd.DataFrame, figsize: Tuple[int, int] = (12, 5), save_path: Optional[str] = None) -> None:
    """Visualiza la distribución de categorías ICA mediante un gráfico de barras.
    
    Parámetros:
        df: DataFrame con los datos (debe incluir columna 'ica_category').
        figsize: Tamaño de la figura.
        save_path: Ruta para guardar la imagen (si se proporciona).
    """
    if 'ica_category' not in df.columns:
        print("❌ La columna 'ica_category' no existe. Ejecuta add_ica_category() primero.")
        return

    orden_ica = ["Buena", "Moderada", "Dañina para grupos sensibles", "Dañina", "Muy dañina", "Peligrosa"]
    counts = df['ica_category'].value_counts().reindex(orden_ica, fill_value=0)

    fig, ax = plt.subplots(figsize=figsize)
    colors = [ICA_COLORS.get(cat, '#CCCCCC') for cat in counts.index]

    # Gráfico de barras
    ax.barh(range(len(counts)), counts.values, color=colors, edgecolor='black', alpha=0.8)
    ax.set_yticks(range(len(counts)))
    ax.set_yticklabels(counts.index, ha='right', fontsize=9)
    ax.set_xlabel("Frecuencia", fontsize=11)
    ax.set_title("Distribución de Categorías ICA", fontsize=13, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # Agregar valores y porcentajes
    total = counts.sum()
    for i, v in enumerate(counts.values):
        ax.text(v + 1, i, f"{v} ({v / total:.1%})", va='center', fontsize=8)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_correlation_matrix(df: pd.DataFrame, columnas: Optional[List[str]] = None, figsize: Tuple[int, int] = (10, 8), save_path: Optional[str] = None) -> None:
    """Matriz de correlación entre contaminantes.
    Parámetros:
        df: DataFrame con los datos.
        columnas: Lista de columnas a incluir (por defecto, todas las de CONTAMINANTES presentes).
        figsize: Tamaño de la figura.
        save_path: Ruta para guardar la imagen (si se proporciona).
    """
    if columnas is None:
        columnas = [c for c in CONTAMINANTES if c in df.columns]
    else:
        columnas = [c for c in columnas if c in df.columns]

    if len(columnas) < 2:
        print("❌ Se necesitan al menos 2 columnas para calcular correlaciones.")
        return

    corr = df[columnas].corr()

    plt.figure(figsize=figsize)
    sns.heatmap(corr, annot=True, cmap='RdYlGn', center=0, fmt=".2f", linewidths=.5, cbar_kws={'label': 'Correlación'})
    plt.title("Matriz de Correlación entre Contaminantes", fontsize=16, fontweight='bold')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_heatmap_hourly(df: pd.DataFrame, columna: str = 'pm2_5', figsize: Tuple[int, int] = (12, 6), save_path: Optional[str] = None) -> None:
    """Heatmap mostrando patrones horarios por día de la semana.
    Parámetros:
        df: DataFrame con los datos.
        columna: Columna a analizar (por defecto 'pm2_5').
        figsize: Tamaño de la figura.
        save_path: Ruta para guardar la imagen (si se proporciona).
    """
    df = ensure_datetime_index(df)
    if columna not in df.columns:
        print(f"❌ La columna '{columna}' no existe en el DataFrame.")
        return

    df_temp = df.copy()
    df_temp['dow'] = df_temp.index.dayofweek
    df_temp['hour'] = df_temp.index.hour
    pivot = df_temp.pivot_table(values=columna, index='dow', columns='hour', aggfunc='mean')

    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    pivot.index = [dias[i] for i in pivot.index]

    plt.figure(figsize=figsize)
    sns.heatmap(pivot, cmap='YlOrRd', annot=False, fmt='.1f', cbar_kws={'label': f'{columna.upper()} (µg/m³)'})
    plt.title(f'Patrón Horario de {columna.upper()} por Día de la Semana', fontsize=14, fontweight='bold')
    plt.xlabel('Hora del Día', fontsize=12)
    plt.ylabel('Día de la Semana', fontsize=12)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_top_n_contaminated_days(estacion: dp.EstacionCalidadAire, columna: str = 'pm2_5', n: int = 10, 
                                figsize: Tuple[int, int] = (12, 6), save_path: Optional[str] = None) -> None:
    """Gráfico de barras horizontales con los N días más contaminados de una estación."""
    if columna not in estacion.df.columns:
        print(f"❌ La columna '{columna}' no existe en los datos de la estación '{estacion.nombre}'.")
        return

    top_dias = estacion.top_n_dias_mas_contaminados(columna, n)
    
    plt.figure(figsize=figsize)
    colors = plt.cm.Reds(np.linspace(0.4, 0.9, n))
    plt.barh(range(len(top_dias)), top_dias[columna], color=colors, edgecolor='black', alpha=0.8)
    plt.yticks(range(len(top_dias)), [str(d) for d in top_dias['date'].dt.date])
    plt.xlabel(f"{columna.upper()} (µg/m³)", fontsize=12)
    plt.ylabel("Fecha", fontsize=12)
    plt.title(f"Top {n} Días más contaminados en {estacion.nombre} ({columna.upper()})", fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_scatter_comparison(df: pd.DataFrame, col_x: str = 'pm2_5', col_y: str = 'pm10', figsize: Tuple[int, int] = (10, 6), save_path: Optional[str] = None) -> None:
    """Scatter plot comparando dos contaminantes.
    Parámetros:
        df: DataFrame con los datos.
        col_x: Columna para el eje X (por defecto 'pm2_5').
        col_y: Columna para el eje Y (por defecto 'pm10').
        figsize: Tamaño de la figura.
        save_path: Ruta para guardar la imagen (si se proporciona).
    """
    if col_x not in df.columns or col_y not in df.columns:
        print(f"❌ Una o ambas columnas no existen en el DataFrame.")
        return

    plt.figure(figsize=figsize)
    if 'ica_category' in df.columns:
        plt.scatter(df[col_x], df[col_y], c=df['ica_category'].map(ICA_COLORS), alpha=0.6, s=20)
    else:
        plt.scatter(df[col_x], df[col_y], alpha=0.6, s=20, c='purple')

    plt.xlabel(f"{col_x.upper()} (µg/m³)", fontsize=12)
    plt.ylabel(f"{col_y.upper()} (µg/m³)", fontsize=12)
    plt.title(f"Relación entre {col_x.upper()} y {col_y.upper()}", fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_correlated_pollutants(df: pd.DataFrame, contaminante:str = 'pm_10', objetivo: str = 'pm2_5', figsize: Tuple[int, int] = (12, 6), regression: bool = True, save_path: Optional[str] = None) -> None:
    """
    Visualiza comparativamente la relación entre contaminantes correlacionados
    y un contaminante objetivo (por defecto, PM2.5).

    Parámetros:
        df: DataFrame con los datos.
        contaminantes: Lista de contaminantes a comparar (por ejemplo ['co', 'no']).
        objetivo: Columna objetivo a correlacionar (por defecto 'pm2_5').
        figsize: Tamaño de la figura.
        regression: Si True, incluye línea de regresión lineal (usando seaborn).
    """
    if contaminante not in df.columns:
        print(f"❌ La columna '{contaminante}' no existe en el DataFrame.")
        return

    if objetivo not in df.columns:
        print(f"❌ La columna objetivo '{objetivo}' no existe en el DataFrame.")
        return

    plt.figure(figsize=figsize)

    if regression:
        sns.regplot(
            x=contaminante,
            y=objetivo,
            data=df,
            scatter_kws={'alpha': 0.5, 's': 25},
            line_kws={'color': 'red', 'linewidth': 2},
            color='steelblue'
        )
    else:
        plt.scatter(df[contaminante], df[objetivo], alpha=0.5, s=25, color='steelblue', edgecolors='none')
    
    plt.title(f"Relación entre {contaminante.upper()} y {objetivo.upper()}", fontsize=14, fontweight='bold')
    plt.xlabel(f"{contaminante.upper()} (µg/m³)", fontsize=12)
    plt.ylabel(f"{objetivo.upper()} (µg/m³)", fontsize=12)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

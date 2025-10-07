"""
Módulo: Procesamiento y Limpieza de Datos
--------------------------------------------
Limpia, transforma y prepara el dataset. Incluye la clasificación automática del Índice de Calidad del Aire (ICA)
basado en los valores de PM2.5, conforme a las categorías internacionales.
"""

import pandas as pd
import numpy as np

# Contaminantes comunes en dataset de calidad del aire
CONTAMINANTES = ['co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3']

def quality_report(df_idx: pd.DataFrame) -> dict:
    """
    Genera un informe de calidad del DataFrame:
        - Número de filas y columnas.
        - Número de duplicados.
        - Frecuencia inferida de los índices de tiempo.
        - Valores faltantes por columna.
    Return: 
        dict: Informe de calidad del DataFrame.
    """
    idx = df_idx.index
    try: freq = pd.infer_freq(idx)
    except Exception: freq = None
    return {
        "rows": int(df_idx.shape[0]),
        "cols": int(df_idx.shape[1]),
        "duplicates": int(idx.duplicated().sum()),
        "inferred_freq": str(freq),
        "missing": {c: int(df_idx[c].isna().sum()) for c in df_idx.columns}
    }

def resample_agg(df_idx: pd.DataFrame, rule="D", agg="median", cols=CONTAMINANTES) -> pd.DataFrame:
    """
    Reagrega los datos a una frecuencia dada aplicando una función de agregación.
    Parámetros:
        - rule: Frecuencia (por defecto diaria 'D')
        - agg: Método de agregación ('mean', 'median', etc.)
        - cols: Columnas a considerar
    Return:
        pd.DataFrame: DataFrame re-muestreado y agregado.
    """
    cols = [c for c in cols if c in df_idx.columns]
    if not cols: return pd.DataFrame(index=df_idx.index)
    return getattr(df_idx[cols].resample(rule), agg)()

def descriptives(df_idx: pd.DataFrame, cols=CONTAMINANTES) -> pd.DataFrame:
    """
    Genera estadísticas descriptivas de las columnas numéricas del dataset.
    Retorna percentiles 5, 50 y 95 para una visión más completa.
    Parámetros:
        - df_idx: DataFrame de entrada
        - cols: Columnas a considerar
    Return:
        pd.DataFrame: Estadísticas descriptivas de las columnas seleccionadas.
    """
    cols = [c for c in cols if c in df_idx.columns]
    if not cols: return pd.DataFrame()
    d = df_idx[cols].describe(percentiles=[.05,.5,.95]).T
    d = d.rename(columns={"50%":"p50","5%":"p05","95%":"p95"})
    return d[["count","mean","std","min","p05","p50","p95","max"]]


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y transforma los datos:
        - Convierte la columna 'date' a formato datetime.
        - Elimina duplicados y valores faltantes.
        - Extrae columnas temporales: año, mes, día, hora.
        - Reemplaza valores negativos en contaminantes por NaN.
    Parámetros:
        df (pd.DataFrame): DataFrame original.
    Return:
        pd.DataFrame: DataFrame limpio y transformado.
    """
    df = df.copy()

    # Convertir fecha
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df = df.sort_values(by="date")

        # Extraer columnas de tiempo
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["day"] = df["date"].dt.day
        df["hour"] = df["date"].dt.hour

    # Eliminar duplicados
    df = df.drop_duplicates()

    # Reemplazar valores negativos por NaN (no válidos en contaminantes)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].applymap(lambda x: np.nan if x < 0 else x)
    
    if "date" in df.columns: # Establecer 'date' como índice
        df = df.set_index("date")
        df.index.name = "date"

    print("✅ Datos limpios y listos para el análisis.")
    return df


def ica_category(pm25: float) -> str:
    """
    Clasifica el nivel del ICA según los valores de PM2.5.
    Basado en la escala estándar internacional (EPA/OMS).
    Parámetros:
        pm25 (float): Valor de PM2.5 en µg/m³.
    Return:
        str: Categoría del ICA (Buena, Moderada, Dañina para grupos sensibles, Dañina, Muy dañina, Peligrosa).
    """
    if pd.isna(pm25): # Si el valor es NaN
        return np.nan  # Mantener NaN
    elif pm25 <= 50:
        return "Buena"
    elif pm25 <= 100:
        return "Moderada"
    elif pm25 <= 150:
        return "Dañina para grupos sensibles"
    elif pm25 <= 200:
        return "Dañina"
    elif pm25 <= 300:
        return "Muy dañina"
    else:
        return "Peligrosa"


def add_ica_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega una columna 'ICA_Category' al DataFrame según los valores de PM2.5.
    Parámetros:
        df (pd.DataFrame): DataFrame original
    Return:
        pd.DataFrame: DataFrame con la columna adicional 'ica_category'.
    """
    df["ica_category"] = df["pm2_5"].apply(ica_category)
    return df



def get_ica_colors() -> dict:
    """
    Retorna un diccionario con los colores asociados a cada categoría ICA (Índice de Calidad del Aire).
    return:
        dict: Diccionario con categorías ICA como claves y códigos de color HEX como valores.
    """
    return {
        "Buena": "#00E400",               # Verde
        "Moderada": "#FFFF00",            # Amarillo
        "Dañina para grupos sensibles": "#FF7E00",  # Naranja
        "Dañina": "#FF0000",              # Rojo
        "Muy dañina": "#8F3F97",          # Morado
        "Peligrosa": "#7E0023"            # Marrón
    }


def threshold_filter(columna: str, umbral: float):
    """
    Closure que crea una función para filtrar valores mayores a un umbral.
    Parámetros:
        - columna (str): Nombre de la columna a filtrar.
        - umbral (float): Valor umbral para el filtrado.
    Return:
        function: Función que filtra un DataFrame según el umbral dado.
    """
    def filtrar(df: pd.DataFrame):
        return df[df[columna] > umbral]
    return filtrar


class EstacionCalidadAire:
    """
    Clase que representa una estación de monitoreo de calidad del aire.
    Permite obtener resúmenes estadísticos, promedios y registros críticos.
    """

    def __init__(self, nombre: str, df: pd.DataFrame):
        self.nombre = nombre
        self.df = df

    def resumen(self):
        """Devuelve un resumen estadístico general del dataset."""
        return self.df.describe()

    def promedio_por_mes(self, columna: str) -> pd.DataFrame:
        """Calcula el promedio mensual de un contaminante."""
        return self.df.groupby("month")[columna].mean().reset_index()

    def maximo_global(self, columna: str) -> float:
        """Obtiene el valor máximo global de un contaminante."""
        return self.df[columna].max()

    def top_n_dias_mas_contaminados(self, columna: str, n=5) -> pd.DataFrame:
        """Devuelve los N días con mayor concentración de un contaminante."""
        # Agrupar por año, mes y día (es decir, por día calendario)
        grouped = self.df.groupby(['year', 'month', 'day'])[columna].mean().reset_index()
    
        # Reconstruir una columna de fecha para facilitar visualización
        grouped['date'] = pd.to_datetime(grouped[['year', 'month', 'day']])
    
        # Ordenar y tomar los top n (mayor a menor)
        top_n = grouped.sort_values(by=columna, ascending=False).head(n)
    
        # Devolver solo lo relevante
        return top_n[['date', columna]].reset_index(drop=True)



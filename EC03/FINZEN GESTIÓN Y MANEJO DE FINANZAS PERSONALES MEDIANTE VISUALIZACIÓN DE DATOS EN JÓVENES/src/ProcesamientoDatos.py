#====================================================================#
#             2. Procesamiento de datos y filtrado                   #
#====================================================================#
import pandas as pd
def procesar_datos(df_ingresado):
    
    """
    Procesa el DataFrame limpiando datos, eliminando columnas con informacion 
    innecesaria y rellena campos vacios por valores que se pueden utilizar
    para el analisis de los datos.

    Args:
        df_ingresado (pd.DataFrame): DataFrame raw.

    Returns:
        dataframe: df.
    """
    df = df_ingresado.copy()

    # 1. Se descartan columnasDescartar Columnas
    columnas_a_descartar = [
        "Start time",
        "Completion time",
        "Email",
        "Name"
    ]
    df.drop(columns=columnas_a_descartar, inplace=True, errors='ignore')

    # 2. Rellenar Valores Nulos (NaN)

    # a) String/Texto
    df["Correo"] = df["Correo"].fillna("Sin correo")
    df["carrera"] = df["carrera"].fillna("No estudiando")
    df["ocupacion"] = df["ocupacion"].fillna("Sin trabajo")
    df["nombre_negocio"] = df["nombre_negocio"].fillna("Sin negocio")


    # b) Numéricos/Float
    df["porcentaje_ahorro"] = df["porcentaje_ahorro"].fillna(0.0).astype(float)
    df["dificultad_equilibrio"] = df["dificultad_equilibrio"].fillna(0.0).astype(float)

    # 3. Transformación de 'Si'/'No' a 1/0 (Corregido con .map() para evitar FutureWarning)
    columnas_a_codificar = [
        "apoyo_familiar",
        "estudio_actual",
        "trabajo_actual",
        "emprendimiento_actual",
        "tipo_ingreso"
    ]

    mapeo_binario = {'Si': 1, 'No': 0}

    for col in columnas_a_codificar:
        df[col] = df[col].map(mapeo_binario)

        # Llenamos los NaN que provienen de los valores que no eran 'Si' ni 'No' con 0
        df[col] = df[col].fillna(0)

        # Convertimos la columna a entero para consistencia
        df[col] = df[col].astype(int)

    # 4. Eliminación de Duplicados y Cédulas Inválidas

    # a) Asegurar que la columna 'cedula' sea string
    df['cedula'] = df['cedula'].astype(str)

    # b) Filtrar cédulas: Mantenemos solo las cédulas de 10 dígitos (Ecuador).
    df = df[df['cedula'].str.len() == 10]

    # c) Eliminar Duplicados: Se eliminan las filas duplicadas basándose en la columna 'cedula'.
    df.drop_duplicates(subset=['cedula'], keep='first', inplace=True)

    return df


#====================================================================#
#                 3. Filtración y Segmentación                       #
#====================================================================#

def filtrar_datos(df_procesado):
    """
    Filtra el DataFrame procesado para crear y retornar cuatro DataFrames
    segmentados según los requisitos.

    Args:
        df_procesado (pd.DataFrame): DataFrame limpio y transformado.

    Returns:
        tuple: Una tupla con (df_finanzas, df_estadisticas, df_equilibrio, df_tipo_ingreso).
    """

    # Columnas base a incluir en todos los DataFrames
    columnas_base = ["nombre", "apellido", "cedula", "edad", "genero"]

    # 1. DataFrame finanzas
    # Requisito: tipo_ingreso debe ser igual a 1 (personas que SÍ tienen ingresos).
    columnas_finanzas = ["ingresos", "gastos_prioritarios", "gastos_secundarios", "porcentaje_ahorro"]
    df_finanzas = df_procesado[df_procesado['tipo_ingreso'] == 1].copy()
    df_finanzas = df_finanzas[columnas_base + columnas_finanzas]

    # 2. DataFrame estadisticas
    # Requisito: Sin filtrado especial, incluye a todos.
    columnas_estadisticas = ["estudio_actual", "trabajo_actual", "emprendimiento_actual"]
    df_estadisticas = df_procesado[columnas_base + columnas_estadisticas].copy()

    # 3. DataFrame equilibrio
    # Requisito: tipo_ingreso debe ser igual a 1.
    columnas_equilibrio = ["dificultad_equilibrio"]
    df_equilibrio = df_procesado[df_procesado['tipo_ingreso'] == 1].copy()
    df_equilibrio = df_equilibrio[columnas_base + columnas_equilibrio]

    # 4. DataFrame tipo_ingreso
    # Requisito: Solo la columna binaria 'tipo_ingreso'.
    columnas_tipo_ingreso = ["tipo_ingreso"]
    df_tipo_ingreso = df_procesado[columnas_base + columnas_tipo_ingreso].copy()

    return df_finanzas, df_estadisticas, df_equilibrio, df_tipo_ingreso
import os
import numpy as np
import pandas as pd
from src.data_preprocessing import *


def main():
      # Carpeta donde está este script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Rutas seguras
    raw_data_path = os.path.join(current_dir, "data", "diabetes_dataset.csv")
    processed_data_path = os.path.join(current_dir, "data", "processed_diabetes.csv")

    # Mostrar información de depuración
    print("🔹 Buscando archivo CSV en la ruta:")
    print(raw_data_path)
    if not os.path.exists(raw_data_path):
        print("❌ ERROR: No se encontró el archivo CSV en la ruta indicada.")
        print("Por favor verifica que 'diabetes_dataset.csv' esté dentro de la carpeta 'data'.")
        return  # Salir del script si no encuentra el archivo

    # Si existe archivo procesado, cargarlo
    if os.path.exists(processed_data_path):
        print("✅ Archivo procesado encontrado. Cargando dataset existente...")
        df = pd.read_csv(processed_data_path)
    else:
        print("⚙️ Archivo procesado no encontrado. Ejecutando pipeline de preprocesamiento...")
        df = preprocesing_data(raw_data_path, processed_data_path)
        print("💾 Dataset procesado guardado en:", processed_data_path)




    # Show preview of the data
    print("\nData preview:")
    print(df.head())

    print("\n📊 Iniciando análisis estadístico...")
    # Resumen estadístico general
    print("\nESTADÍSTICAS DESCRIPTIVAS DE VARIABLES NUMÉRICAS")
    print(df.describe())

    # Distribución de variables categóricas en porcentajes
    print("\nDISTRIBUCIÓN DE VARIABLES CATEGÓRICAS (%)")
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in cat_cols:
        print(f"{df[col].value_counts(normalize=True).round(3) * 100}\n")

    # Estadísticas adicionales: mediana,moda, rango y coeficiente de variación
    print("\nESTADÍSTICAS AVANZADAS")
    stats_extra = pd.DataFrame({
        'Mediana': df.median(numeric_only=True),
        'Moda': df.mode(numeric_only=True).iloc[0],
        'Rango': df.max(numeric_only=True) - df.min(numeric_only=True),
        'Coef_Variacion': (df.std(numeric_only=True) / df.mean(numeric_only=True)).round(3)
    })
    print(stats_extra)

    # Promedios por grupo de género o estado de diabetes
    print("\nPROMEDIOS POR DE IMC y DIABETES RISK SCORE POR GÉNERO")
    print(df.groupby('Gender')[['Body Mass Index', 'Diabetes Risk Score']].mean().round(2))

    print("\nPROMEDIOS DE EDAD, IMC Y DIABETES RISK SCORE POR ESTADO DE DIABETES")
    print(df.groupby('Diabetes Status')[['Age', 'Body Mass Index', 'Diabetes Risk Score']].mean().round(2))

    # Relación entre fumadores y Diabetes Risk
    print("\nCOMPARACIÓN ENTRE FUMADORES Y NO FUMADORES")
    mean_risk = df.groupby('Smoking')['Diabetes Risk Score'].agg(['mean', 'std', 'count']).round(2)
    mean_risk['error_std'] = (mean_risk['std'] / np.sqrt(mean_risk['count'])).round(2)
    print(mean_risk)

    # Correlación entre IMC y puntuación de riesgo
    print("\nCORRELACIÓN IMC vs RIESGO DE DIABETES ")
    corr_bmi_risk = df['Body Mass Index'].corr(df['Diabetes Risk Score'])
    print(f"Coeficiente de correlación: {corr_bmi_risk:.3f}")

    # Análisis de riesgo promedio por grupo de edad
    print("\nAGRUPACIÓN POR EDADES Y RIESGO DE DIABETES")
    df['Age Group'] = pd.cut(df['Age'], bins=[0,30,45,60,75,100],
                            labels=['<30','30-45','45-60','60-75','75+'])
    risk_by_age = df.groupby('Age Group', observed=True)['Diabetes Risk Score'].mean().round(2)
    print(risk_by_age)



    



if __name__ == "__main__":
    main()
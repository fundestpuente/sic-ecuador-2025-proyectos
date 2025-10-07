import os
import numpy as np
import pandas as pd
from src.data_preprocessing import *


def main():
    raw_data_path = "data/diabetes_dataset.csv"
    processed_data_path = "data/processed_diabetes.csv"

    # Check if processed file already exists
    if os.path.exists(processed_data_path):
        print("✅ Processed file found. Loading existing dataset...")
        df = pd.read_csv(processed_data_path)
    else:
        print("⚙️ No processed file found. Running preprocessing pipeline...")
        df = preprocesing_data(raw_data_path, processed_data_path)
        print("💾 Processed dataset saved to:", processed_data_path)

    # Show preview of the data
    print("\nData preview:")
    print(df.head())

    print("\n📊 Iniciando análisis estadístico...")
    # Resumen estadístico general
    print("\nESTADÍSTICAS DESCRIPTIVAS DE VARIABLES NUMÉRICAS")
    print(df.describe())

    # Distribución de variables categóricas en porcentajes
    print("\nDISTRIBUCIÓN DE VARIABLES CATEGÓRICAS (%): ")
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
    print("\nPROMEDIOS DE IMC y DIABETES RISK SCORE POR GÉNERO")
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
    

    print("\nANÁLISIS DE ANTECEDENTES FAMILIARES MEDIANTE EL DIABETES RISK SCORE: ")
    # Mediana y Media del Riesgo Score por Antecedentes
    family_history_analysis = df.groupby('Family History')['Diabetes Risk Score'].agg(
        ['mean', 'median', 'std']
    )
    # Renombrar para mayor claridad (0=No Historial, 1=Con Historial)
    family_history_analysis.index = ['No Historial Familiar (0)', 'Con Historial Familiar (1)']
    print(family_history_analysis.round(2))
    # Cálculo de la Tasa de Riesgo Aumentada
    mean_risk_no_diabetes = family_history_analysis.loc['No Historial Familiar (0)', 'mean']
    mean_risk_with_diabetes = family_history_analysis.loc['Con Historial Familiar (1)', 'mean']
    risk_increase = ((mean_risk_with_diabetes - mean_risk_no_diabetes) / mean_risk_no_diabetes) * 100
    print(f"\nEl riesgo promedio de diabetes (nivel de amenaza) es un {risk_increase:.1f}% mayor en la población con antecedentes familiares.")


    # ACTIVIDAD FISICA Y RIESGO DE DIABETES
    print("\nRELACIÓN ENTRE RIESGO DE DIABETES Y ACTIVIDAD FÍSICA")
    df['Activity Level'] = pd.qcut(
    df['Physical Activity'], 
    q=3, 
    labels=['Baja', 'Media', 'Alta'], 
    duplicates='drop'
    )

    #CÁLCULO DE MÉTRICAS CLAVE POR NIVEL DE ACTIVIDAD
    activity_analysis = df.groupby('Activity Level', observed=True).agg(
        # Riesgo Promedio (Mean_Risk)
        Riesgo_Promedio=('Diabetes Risk Score', 'mean'),
        # IMC Promedio (Mean_IMC)
        IMC_Promedio=('Body Mass Index', 'mean'),
        # Prevalencia de Diabetes (calculando la media de la columna binaria 0/1)
        Prevalencia_Diabetes=('Diabetes Status', 'mean')
    )

    # Convierte la prevalencia a un porcentaje legible
    activity_analysis['Prevalencia_Diabetes (%)'] = (activity_analysis['Prevalencia_Diabetes'] * 100).round(1)
    # Redondea y presenta el resultado final
    activity_analysis = activity_analysis.drop(columns=['Prevalencia_Diabetes']).round(2)
    print(activity_analysis)
    # Análisis de la Brecha de Riesgo: Cuantificar cuánto peor es el grupo 'Baja' que el grupo 'Alta'
    risk_low = activity_analysis.loc['Baja', 'Riesgo_Promedio']
    risk_high = activity_analysis.loc['Alta', 'Riesgo_Promedio']
    risk_difference_percent = ((risk_low - risk_high) / risk_high) * 100
    print(f"\n *El grupo de Baja Actividad tiene un riesgo promedio de diabetes (nivel de amenaza) un {risk_difference_percent:.1f}% mayor que el de Alta Actividad.")
        

    print("\nPREVALENCIA DE DIABETES (%) POR ESTADO DE PESO (IMC)")
    # 1. Definir grupos de IMC
    bins_imc = [df['Body Mass Index'].min(), 25, 30, df['Body Mass Index'].max()]
    labels_imc = ['Bajo/Normal (<25)', 'Sobrepeso (25-30)', 'Obeso (>30)']
    df['IMC_Category'] = pd.cut(df['Body Mass Index'], bins=bins_imc, labels=labels_imc, right=False, include_lowest=True)
    # 2. Calcular la Prevalencia de Diabetes
    prevalence_analysis = df.groupby('IMC_Category', observed=True)['Diabetes Status'].mean().sort_values()
    # 3. Convertir a Porcentaje y Formatear
    prevalence_percent = (prevalence_analysis * 100).round(2)
    prevalence_percent.name = 'Prevalencia de Diabetes (%)'

    print(prevalence_percent)
    
if __name__ == "__main__":
    main()
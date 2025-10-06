import pandas as pd
import numpy as np


def convert_to_df(path: str) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.

    Args:
        path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the loaded data.
    """
    return pd.read_csv(path)

def filter_relevant_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Select and rename relevant columns related to diabetes risk factors.

    Args:
        df (pd.DataFrame): Original DataFrame containing all dataset columns.

    Returns:
        pd.DataFrame: Filtered and renamed DataFrame with only relevant columns.
    """
    columns_mapping = {
        'age': 'Age',                                              # Age affects diabetes risk
        'gender': 'Gender',                                        # Gender affects risk patterns
        'ethnicity': 'Ethnicity',                                  # Ethnicity can influence medication response and risk
        'smoking_status': 'Smoking',                               # Modifiable lifestyle factor
        'alcohol_consumption_per_week': 'Alcohol per Week',        # Modifiable lifestyle factor
        'physical_activity_minutes_per_week': 'Physical Activity', # Lifestyle factor, impacts risk
        'diet_score': 'Diet',                                      # Nutrition quality
        'sleep_hours_per_day': 'Sleep Hours',                      # Lifestyle factor, affects metabolism
        'screen_time_hours_per_day': 'Screen Time',                # Sedentary behavior indicator
        'family_history_diabetes': 'Family History',               # Genetic risk factor
        'hypertension_history': 'Hypertension',                    # Comorbidity increasing diabetes risk
        'cardiovascular_history': 'Heart Disease History',         # Comorbidity affecting overall risk
        'bmi': 'Body Mass Index',                                  # Body mass index, modifiable risk factor
        'waist_to_hip_ratio': 'Waist to Hip Ratio',                # Body fat distribution, risk indicator
        'diabetes_risk_score': 'Diabetes Risk Score',              # Overall understandable risk summary
        'diagnosed_diabetes': 'Diabetes Status'                    # Current diabetes status
    }

    df_clean = df[list(columns_mapping.keys())].copy()
    df_clean.rename(columns=columns_mapping, inplace=True)

    df_clean["Gender"] = df_clean["Gender"].astype("category")
    df_clean["Ethnicity"] = df_clean["Ethnicity"].astype("category")
    df_clean["Smoking"] = df_clean["Smoking"].astype("category")

    return df_clean
    

def clean_duplicates_and_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows and handle missing values based on data type and skewness.

    Args:
        df (pd.DataFrame): Input DataFrame with potential duplicates and missing values.

    Returns:
        pd.DataFrame: Cleaned DataFrame with duplicates removed and missing values imputed.
    """
    df_clean = df.drop_duplicates()

    numeric_cols = df_clean.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_cols:
        if abs(df_clean[col].skew()) > 2:
            impute_value = df_clean[col].median()
        else:
            impute_value = df_clean[col].mean()
        df_clean[col].fillna(impute_value, inplace=True)

    categorical_cols = df_clean.select_dtypes(include=['object', 'category']).columns
    for col in categorical_cols:
        impute_value = df_clean[col].mode()[0] if not df_clean[col].mode().empty else 'Unknown'
        df_clean[col].fillna(impute_value, inplace=True)

    return df_clean

def save_to_csv(df: pd.DataFrame, output_path: str) -> None:
    """
    Save a pandas DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): DataFrame to be saved.
        output_path (str): Destination file path where the CSV will be stored.

    Returns:
        None
    """
    df.to_csv(output_path, index=False)


def preprocesing_data(raw_path, output_path) -> pd.DataFrame:
    """
    Load, filter, and clean the diabetes dataset to prepare it for analysis.

    Returns:
        pd.DataFrame: Fully preprocessed DataFrame ready for analysis or modeling.
    """
    df = convert_to_df(raw_path)
    df_filter = filter_relevant_columns(df)
    df_clean = clean_duplicates_and_missing_values(df_filter)
    save_to_csv(df_clean, output_path)

    return df_clean


__all__ = ["preprocesing_data"]
import os
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


if __name__ == "__main__":
    main()
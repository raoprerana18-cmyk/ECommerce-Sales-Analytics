
import pandas as pd
from pathlib import Path

# ==========================================
# 1. PROJECT FOLDER LOCATIONS
# ==========================================

project_folder = Path(__file__).resolve().parent.parent

raw_folder = project_folder / "01_Raw_Data"
clean_folder = project_folder / "02_Cleaned_Data"

# Create cleaned data folder if it does not exist
clean_folder.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. DATASET FILES
# ==========================================

files = [
    "customers.csv",
    "products.csv",
    "orders.csv",
    "order_items.csv",
    "returns.csv"
]

# ==========================================
# 3. DATE COLUMNS
# ==========================================

date_columns = {
    "customers.csv": ["signup_date", "first_order_date"],
    "products.csv": ["launch_date"],
    "orders.csv": ["order_date"],
    "returns.csv": ["return_date"]
}

# ==========================================
# 4. LOAD AND CLEAN DATASETS
# ==========================================

for file in files:

    print("\n" + "=" * 60)
    print("CLEANING:", file)
    print("=" * 60)

    # Load original dataset
    df = pd.read_csv(raw_folder / file)

    # Remove unnecessary spaces from column names
    df.columns = df.columns.str.strip()

    # Remove leading and trailing spaces in text columns
    text_columns = df.select_dtypes(include=["object", "str"]).columns

    for column in text_columns:
        df[column] = df[column].str.strip()

    # Standardise currency codes
    if "currency_code" in df.columns:
        df["currency_code"] = df["currency_code"].str.upper()

    # Convert date columns
    for column in date_columns.get(file, []):
        df[column] = pd.to_datetime(
            df[column],
            format="mixed",
            dayfirst=True,
            errors="coerce"
        )

    # Check duplicate records
    duplicates = df.duplicated().sum()

    # Check missing values
    missing = df.isnull().sum().sum()

    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Duplicate rows:", duplicates)
    print("Missing values:", missing)

    # Save cleaned dataset
    output_path = clean_folder / file
    df.to_csv(output_path, index=False, date_format="%Y-%m-%d")

    print("Saved:", output_path)

# ==========================================
# 5. COMPLETION MESSAGE
# ==========================================

print("\nALL FIVE DATASETS PROCESSED!")
print("Cleaned files saved in 02_Cleaned_Data")

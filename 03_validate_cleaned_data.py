
import pandas as pd
from pathlib import Path

# Project folder
project_folder = Path(__file__).resolve().parent.parent
clean_folder = project_folder / "02_Cleaned_Data"

# Date columns in each dataset
date_columns = {
    "customers.csv": ["signup_date", "first_order_date"],
    "products.csv": ["launch_date"],
    "orders.csv": ["order_date"],
    "returns.csv": ["return_date"]
}

# Expected row counts
expected_rows = {
    "customers.csv": 3000,
    "products.csv": 345,
    "orders.csv": 14000,
    "order_items.csv": 29671,
    "returns.csv": 2433
}

for file, expected in expected_rows.items():

    print("\n" + "=" * 55)
    print("VALIDATING:", file)
    print("=" * 55)

    df = pd.read_csv(clean_folder / file)

    # Check row count
    print("Actual rows:", len(df))
    print("Expected rows:", expected)
    print("Row count correct:", len(df) == expected)

    # Check date columns
    for column in date_columns.get(file, []):

        df[column] = pd.to_datetime(
            df[column],
            format="mixed",
            dayfirst=True,
            errors="coerce"
        )

        print(
            column,
            "date type:", df[column].dtype,
            "| Missing:", df[column].isna().sum()
        )

    print("Duplicate rows:", df.duplicated().sum())

print("\nVALIDATION COMPLETED!")

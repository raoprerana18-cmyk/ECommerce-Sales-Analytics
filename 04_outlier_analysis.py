
import pandas as pd
from pathlib import Path

# Locate cleaned data
project_folder = Path(__file__).resolve().parent.parent
clean_folder = project_folder / "02_Cleaned_Data"

# Load datasets
orders = pd.read_csv(clean_folder / "orders.csv")
items = pd.read_csv(clean_folder / "order_items.csv")
products = pd.read_csv(clean_folder / "products.csv")

# Columns to investigate
checks = {
    "Orders": (orders, ["order_total_usd", "delivery_days"]),
    "Order Items": (items, ["quantity", "line_total_usd", "line_profit_usd"]),
    "Products": (products, ["list_price_usd", "unit_cost_usd", "weight_kg"])
}

for name, (df, columns) in checks.items():

    print("\n" + "=" * 55)
    print("OUTLIER ANALYSIS:", name)
    print("=" * 55)

    for column in columns:

        print("\nColumn:", column)

        print(df[column].describe())

        # IQR calculation
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)

        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = df[
            (df[column] < lower) |
            (df[column] > upper)
        ]

        print("Lower limit:", lower)
        print("Upper limit:", upper)
        print("Potential outliers:", len(outliers))

print("\nOUTLIER ANALYSIS COMPLETED!")
print("\nTOP 10 HIGHEST ORDER VALUES")
print("=" * 50)

print("\nORDERS DATASET COLUMNS")
print(orders.columns.tolist())

print("\nTOP 10 HIGHEST ORDER VALUES")
print("=" * 50)

top_orders = orders.nlargest(10, "order_total_usd")

print(top_orders.to_string(index=False))
print("\nORDERS DATASET COLUMNS")
print(orders.columns.tolist())
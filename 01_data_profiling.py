
import pandas as pd
from pathlib import Path

# Locate project and raw data folders
project_folder = Path(__file__).resolve().parent.parent
data_folder = project_folder / "01_Raw_Data"

# List of CSV files
files = [
    "customers.csv",
    "products.csv",
    "orders.csv",
    "order_items.csv",
    "returns.csv"
]

# Perform data profiling
for file in files:

    print("\n" + "=" * 60)
    print("DATASET:", file)
    print("=" * 60)

    file_path = data_folder / file

    df = pd.read_csv(file_path)

    print("\nRows and Columns:", df.shape)

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nFirst Five Records:")
    print(df.head())

    print("\nData Types and Information:")
    df.info()

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nDuplicate Rows:", df.duplicated().sum())

print("\nALL DATASETS PROFILED SUCCESSFULLY!")

# Investigating missing values in Orders

orders = pd.read_csv(data_folder / "orders.csv")

print("\n--- ORDER STATUS ANALYSIS ---")
print(orders["order_status"].value_counts())

print("\n--- MISSING DELIVERY DAYS BY ORDER STATUS ---")
print(
    orders[orders["delivery_days"].isnull()]
    ["order_status"]
    .value_counts()
)

# Investigating missing customer first order dates

customers = pd.read_csv(data_folder / "customers.csv")

print("\n--- CUSTOMERS WITH MISSING FIRST ORDER DATE ---")
print(
    customers[customers["first_order_date"].isnull()]
    [["customer_id", "lifetime_orders", "lifetime_spend_usd"]]
    .head(10)
)

# Investigate all customers with missing first order dates

customers = pd.read_csv(data_folder / "customers.csv")

missing_customers = customers[
    customers["first_order_date"].isnull()
]

print("\n--- CUSTOMER MISSING DATE ANALYSIS ---")

print("Total missing first order dates:",
      len(missing_customers))

print("\nLifetime Orders Distribution:")
print(missing_customers["lifetime_orders"].value_counts())

print("\nTotal Lifetime Spend:")
print(missing_customers["lifetime_spend_usd"].describe())

print("\nCustomers with purchases but missing first order date:")

print(
    missing_customers[
        missing_customers["lifetime_orders"] > 0
    ][["customer_id", "lifetime_orders", "lifetime_spend_usd"]]
)

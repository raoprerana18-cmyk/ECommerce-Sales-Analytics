
import pandas as pd
from pathlib import Path

# Project folder paths
project_folder = Path(__file__).resolve().parent.parent
clean_folder = project_folder / "02_Cleaned_Data"

# Load cleaned datasets
orders = pd.read_csv(clean_folder / "orders.csv")
items = pd.read_csv(clean_folder / "order_items.csv")
products = pd.read_csv(clean_folder / "products.csv")

print("=" * 60)
print("DATA QUALITY CHECKS")
print("=" * 60)

# 1. Check order values
print("\n1. ORDER DATA CHECKS")

print("Zero or negative order totals:",
      (orders["order_total_usd"] <= 0).sum())

print("Zero or negative exchange rates:",
      (orders["fx_rate_to_usd"] <= 0).sum())

print("Negative item counts:",
      (orders["items_count"] < 0).sum())

# 2. Check order item values
print("\n2. ORDER ITEMS DATA CHECKS")

print("Zero or negative quantities:",
      (items["quantity"] <= 0).sum())

print("Negative line totals:",
      (items["line_total_usd"] < 0).sum())

print("Negative line profits:",
      (items["line_profit_usd"] < 0).sum())

# 3. Check product values
print("\n3. PRODUCT DATA CHECKS")

print("Zero or negative list prices:",
      (products["list_price_usd"] <= 0).sum())

print("Zero or negative unit costs:",
      (products["unit_cost_usd"] <= 0).sum())

print("Zero or negative product weights:",
      (products["weight_kg"] <= 0).sum())

print("\nDATA QUALITY CHECK COMPLETED!")

print("\n" + "=" * 60)
print("INVESTIGATING NEGATIVE PROFIT RECORDS")
print("=" * 60)

negative_profit = items[items["line_profit_usd"] < 0]

print("Total negative-profit records:", len(negative_profit))

print("\nFirst 10 negative-profit records:")

print(
    negative_profit.head(10).to_string(index=False)
)

print("\nNegative profit summary:")

print(negative_profit["line_profit_usd"].describe())

print("\n" + "=" * 60)
print("CHECKING PROFIT CALCULATION")
print("=" * 60)

# Calculate expected profit using the current fields
items["calculated_profit"] = (
    items["line_total_usd"] - items["unit_cost_usd"]
)

# Compare with recorded profit
items["profit_difference"] = (
    items["line_profit_usd"] - items["calculated_profit"]
)

print("\nProfit calculation differences:")
print(items["profit_difference"].describe())

print(
    "\nRecords where recorded and calculated profit differ:",
    (items["profit_difference"].abs() > 0.01).sum()
)

print("\nSample records with differences:")

print(
    items.loc[
        items["profit_difference"].abs() > 0.01,
        [
            "order_item_id",
            "quantity",
            "line_total_usd",
            "unit_cost_usd",
            "line_profit_usd",
            "calculated_profit"
        ]
    ].head(10).to_string(index=False)
)

print("\n" + "=" * 60)
print("VERIFYING PROFIT USING QUANTITY")
print("=" * 60)

items["calculated_profit_v2"] = (
    items["line_total_usd"]
    - (items["unit_cost_usd"] * items["quantity"])
)

items["profit_difference_v2"] = (
    items["line_profit_usd"] - items["calculated_profit_v2"]
)

print("\nAlternative calculation differences:")
print(items["profit_difference_v2"].describe())

print(
    "\nRecords with differences:",
    (items["profit_difference_v2"].abs() > 0.01).sum()
)

print("\nFirst 10 comparison records:")

print(
    items[
        [
            "order_item_id",
            "quantity",
            "line_total_usd",
            "unit_cost_usd",
            "line_profit_usd",
            "calculated_profit_v2"
        ]
    ].head(10).to_string(index=False)
)

print("\n" + "=" * 60)
print("FINAL TWO PROFIT MISMATCH RECORDS")
print("=" * 60)

mismatches = items[
    items["profit_difference_v2"].abs() > 0.01
]

print(
    mismatches[
        [
            "order_item_id",
            "quantity",
            "line_total_usd",
            "unit_cost_usd",
            "line_profit_usd",
            "calculated_profit_v2",
            "profit_difference_v2"
        ]
    ].to_string(index=False)
)

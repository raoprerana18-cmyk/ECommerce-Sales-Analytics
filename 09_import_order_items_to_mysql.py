
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, types
from sqlalchemy.engine import URL

# Locate the project folder
project_folder = Path(__file__).resolve().parent.parent
clean_folder = project_folder / "02_Cleaned_Data"

# Load the cleaned order_items CSV
order_items = pd.read_csv(clean_folder / "order_items.csv")

print("Rows found:", len(order_items))
print("Columns:", order_items.columns.tolist())

# Connect to MySQL
connection_url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password="MyRoot@123",
    host="localhost",
    port=3306,
    database="ecommerce_analytics"
)

engine = create_engine(connection_url)

# Define column data types
column_types = {
    "order_item_id": types.VARCHAR(30),
    "order_id": types.VARCHAR(30),
    "product_id": types.VARCHAR(30),
    "quantity": types.Integer(),
    "unit_price_local": types.Float(),
    "line_total_local": types.Float(),
    "line_total_usd": types.Float(),
    "unit_cost_usd": types.Float(),
    "line_profit_usd": types.Float(),
    "discount_local": types.Float(),
    "currency_code": types.VARCHAR(10)
}

# Import into MySQL
order_items.to_sql(
    name="order_items",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=1000,
    dtype=column_types
)

print("Order items imported successfully!")
print("Records imported:", len(order_items))

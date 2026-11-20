
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, types

# Project folder
project_folder = Path(__file__).resolve().parent.parent
clean_folder = project_folder / "02_Cleaned_Data"

# Read cleaned orders CSV
orders = pd.read_csv(clean_folder / "orders.csv")

# Convert date column
orders["order_date"] = pd.to_datetime(
    orders["order_date"], errors="coerce"
)

# MySQL connection
# Replace YOUR_PASSWORD with your MySQL password

# MySQL connection
from sqlalchemy.engine import URL

connection_url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password="MyRoot@123",
    host="localhost",
    port=3306,
    database="ecommerce_analytics"
)

engine = create_engine(connection_url)


# Column data types
column_types = {
    "order_id": types.VARCHAR(30),
    "customer_id": types.VARCHAR(30),
    "order_date": types.Date(),
    "order_month": types.VARCHAR(10),
    "sales_channel": types.VARCHAR(50),
    "device_type": types.VARCHAR(30),
    "payment_method": types.VARCHAR(50),
    "shipping_country": types.VARCHAR(60),
    "shipping_region": types.VARCHAR(50),
    "currency_code": types.VARCHAR(10),
    "fx_rate_to_usd": types.Float(),
    "items_count": types.Integer(),
    "gross_amount_local": types.Float(),
    "discount_local": types.Float(),
    "shipping_fee_local": types.Float(),
    "tax_local": types.Float(),
    "order_total_local": types.Float(),
    "order_total_usd": types.Float(),
    "order_status": types.VARCHAR(30),
    "delivery_days": types.Float()
}

# Replace incomplete orders table with complete data
orders.to_sql(
    name="orders",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=1000,
    dtype=column_types
)

print("Orders imported successfully!")
print("Records imported:", len(orders))

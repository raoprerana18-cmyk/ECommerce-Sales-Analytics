
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, types
from sqlalchemy.engine import URL

# Locate project folder
project_folder = Path(__file__).resolve().parent.parent
clean_folder = project_folder / "02_Cleaned_Data"

# Load cleaned returns data
returns = pd.read_csv(clean_folder / "returns.csv")

print("Rows found:", len(returns))
print("Columns:", returns.columns.tolist())

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
    "return_id": types.VARCHAR(30),
    "order_id": types.VARCHAR(30),
    "order_item_id": types.VARCHAR(30),
    "customer_id": types.VARCHAR(30),
    "product_id": types.VARCHAR(30),
    "return_date": types.Date(),
    "return_reason": types.VARCHAR(100),
    "return_status": types.VARCHAR(50),
    "refund_amount_local": types.Float(),
    "refund_amount_usd": types.Float(),
    "currency_code": types.VARCHAR(10),
    "shipping_country": types.VARCHAR(60),
    "shipping_region": types.VARCHAR(50),
    "sales_channel": types.VARCHAR(50),
    "device_type": types.VARCHAR(30)
}

returns.to_sql(
    name="returns",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=1000,
    dtype=column_types
)

print("Returns imported successfully!")
print("Records imported:", len(returns))

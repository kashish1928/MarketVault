import pandas as pd
from sqlalchemy import create_engine

# Connect to PostgreSQL
engine = create_engine("postgresql://airflow:airflow@localhost:5433/stockdb")

# Sample data
df = pd.DataFrame({
    'ticker': ['AAPL', 'GOOG', 'MSFT'],
    'price': [150.12, 2800.45, 299.99]
})

# Write to DB
df.to_sql('test_stock_prices', engine, if_exists='replace', index=False)

# Read back
result = pd.read_sql("SELECT * FROM test_stock_prices", engine)
print(result)

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine

def fetch_and_store():
    df = yf.download("AAPL", start="2023-01-01", end="2023-12-31")
    engine = create_engine("postgresql://airflow:airflow@postgres:5432/stockdb")
    df.to_sql("raw_stock_data", engine, if_exists="replace")

with DAG(
    dag_id="stock_ingestion_test_dag",
    start_date=datetime(2023, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:
    task = PythonOperator(
        task_id="fetch_stock_data",
        python_callable=fetch_and_store
    )

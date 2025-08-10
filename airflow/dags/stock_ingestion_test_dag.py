from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
from airflow.utils.log.logging_mixin import LoggingMixin

def fetch_and_store():
    logger = LoggingMixin().log
    try:
        # Fetch data
        df = yf.download(["AAPL","AMD","NVDA"], period='1mo')
        if df.empty:
            logger.info("No data returned for AAPL. Skipping database write.")
            return

        # Connect to database
        engine = create_engine("postgresql://airflow:airflow@postgres:5432/stockdb")

        # Write to database
        try:
            df.to_sql("raw_stock_data", engine, schema="test", if_exists="replace", index=False)
            logger.info("Data successfully written to raw_stock_data table.")
        except SQLAlchemyError as db_err:
            logger.info(f"Database error during to_sql: {db_err}")
            raise

    except Exception as e:
        logger.info(f"Unexpected error in fetch_and_store: {e}")
        raise


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

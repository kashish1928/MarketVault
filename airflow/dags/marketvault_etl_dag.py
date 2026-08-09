from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.log.logging_mixin import LoggingMixin
import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

default_args = {
    'owner': 'marketvault',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}


def extract_and_load_raw_stocks():
    """
    Downloads historical stock data for top market tickers using yfinance
    and loads the raw dataset into PostgreSQL (public.raw_stock_data).
    """
    logger = LoggingMixin().log
    tickers = ["AAPL", "NVDA", "MSFT", "GOOGL", "AMZN", "TSLA", "META"]
    logger.info(f"Starting extraction for tickers: {tickers}")

    # Fetch 6 months of historical stock data
    df = yf.download(tickers, period='6mo', group_by='ticker', auto_adjust=False)

    if df.empty:
        raise ValueError("yfinance returned an empty DataFrame! Ingestion aborted.")

    records = []
    # Parse multi-ticker DataFrame
    for ticker in tickers:
        if ticker in df.columns.levels[0]:
            ticker_df = df[ticker].copy()
            ticker_df = ticker_df.reset_index()
            ticker_df['ticker'] = ticker

            # Rename columns to lowercase standard names
            ticker_df = ticker_df.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })

            # Filter relevant columns
            valid_cols = ['date', 'ticker', 'open', 'high', 'low', 'close', 'volume']
            ticker_df = ticker_df[[c for c in valid_cols if c in ticker_df.columns]]
            ticker_df = ticker_df.dropna(subset=['close'])
            records.append(ticker_df)

    if not records:
        raise ValueError("No valid stock price records parsed from download.")

    final_df = pd.concat(records, ignore_index=True)
    logger.info(f"Successfully processed {len(final_df)} raw stock records.")

    # Connect to PostgreSQL inside Docker network
    db_url = "postgresql://airflow:airflow@postgres:5432/stockdb"
    engine = create_engine(db_url)

    try:
        final_df.to_sql(
            "raw_stock_data",
            engine,
            schema="public",
            if_exists="replace",
            index=False
        )
        logger.info("Successfully replaced public.raw_stock_data in PostgreSQL.")
    except SQLAlchemyError as err:
        logger.error(f"Failed to write stock data to Postgres: {err}")
        raise


with DAG(
    dag_id="marketvault_etl_dag",
    default_args=default_args,
    description="End-to-end stock market ETL: Raw YFinance ingestion -> dbt transformations -> dbt tests",
    schedule="@daily",
    catchup=False,
    tags=["production", "marketvault", "etl", "dbt"]
) as dag:

    ingest_raw_stock_data = PythonOperator(
        task_id="ingest_raw_stock_data",
        python_callable=extract_and_load_raw_stocks
    )

    run_dbt_models = BashOperator(
        task_id="run_dbt_models",
        bash_command="dbt run --project-dir /opt/airflow/dbt --profiles-dir /opt/airflow/dbt",
        env={
            "DBT_HOST": "postgres",
            "DBT_PORT": "5432",
            "POSTGRES_USER": "airflow",
            "POSTGRES_PASSWORD": "airflow",
            "POSTGRES_DB": "stockdb"
        }
    )

    test_dbt_models = BashOperator(
        task_id="test_dbt_models",
        bash_command="dbt test --project-dir /opt/airflow/dbt --profiles-dir /opt/airflow/dbt",
        env={
            "DBT_HOST": "postgres",
            "DBT_PORT": "5432",
            "POSTGRES_USER": "airflow",
            "POSTGRES_PASSWORD": "airflow",
            "POSTGRES_DB": "stockdb"
        }
    )

    ingest_raw_stock_data >> run_dbt_models >> test_dbt_models

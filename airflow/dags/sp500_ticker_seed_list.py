from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from airflow.utils.log.logging_mixin import LoggingMixin


def get_sp500_tickers():
    """
    This DAG gets all the S&P 500 stock tickers
    """
    logger = LoggingMixin().log
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    df = tables[0]
    tickers = df[['Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry', 'Headquarters Location']]
    engine = create_engine("postgresql://airflow:airflow@postgres:5432/stockdb")
    try:
        tickers.to_sql(
            "sp500_seed_list",
            engine,
            schema="raw",
            if_exists="replace",
            index=False)
        logger.info("Data successfully written to sp500_seed_list.")
    except SQLAlchemyError as db_err:
        logger.info(f"Database error during to_sql: {db_err}")
        raise


with DAG(
    dag_id="sp_500_ticker_seed_list",
    start_date=datetime(2023, 1, 1),
    schedule_interval="@quarterly",
    catchup=False
) as dag:
    task = PythonOperator(
        task_id="get_sp500_tickers",
        python_callable=get_sp500_tickers
    )

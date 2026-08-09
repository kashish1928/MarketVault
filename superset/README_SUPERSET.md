# Apache Superset Setup & Visualizations Guide

This guide explains how to access Apache Superset, register datasets, and create visualizations for stock market analytics in MarketVault.

---

## 1. Accessing Apache Superset

Once containers are launched via `make build` or `docker compose up -d`:
- **Web UI URL**: [http://localhost:8088](http://localhost:8088)
- **Admin Credentials**:
  - **Username**: `admin`
  - **Password**: `admin`

---

## 2. PostgreSQL Database Connection

The database connection `MarketVault StockDB` is automatically registered by the initialization script (`superset/docker-init.sh`).

If you ever need to add or update it manually:
1. Navigate to **Settings** (top-right gear icon) $\rightarrow$ **Database Connections**.
2. Click **+ Database**.
3. Select **PostgreSQL**.
4. Enter the SQLAlchemy URI:
   ```
   postgresql+psycopg2://airflow:airflow@postgres:5432/stockdb
   ```
5. Click **Test Connection** and **Save**.

---

## 3. Registering the Analytics Dataset

1. In Superset, go to **Datasets** $\rightarrow$ Click **+ Dataset**.
2. Select **Database**: `MarketVault StockDB`.
3. Select **Schema**: `public`.
4. Select **Table**: `fct_daily_stock_metrics`.
5. Click **Create Dataset and Create Chart**.

---

## 4. Recommended Visualizations

### Chart 1: Stock Closing Price Trend (Line Chart)
- **Chart Type**: Line Chart
- **Dataset**: `fct_daily_stock_metrics`
- **Time Column**: `stock_date`
- **Time Grain**: Day
- **Dimensions / Group By**: `ticker`
- **Metrics**: `AVG(close_price)`
- **Description**: Displays comparative price performance over time for AAPL, NVDA, MSFT, GOOGL, AMZN, TSLA, and META.

### Chart 2: 7-Day Moving Average vs Close Price (Line Chart)
- **Chart Type**: Line Chart
- **Dataset**: `fct_daily_stock_metrics`
- **Metrics**: `AVG(close_price)`, `AVG(moving_avg_7d)`
- **Filters**: `ticker = NVDA` (or any stock of interest)
- **Description**: Visualizes trend momentum and moving average crossovers.

### Chart 3: Trading Volume Comparison (Bar Chart)
- **Chart Type**: Bar Chart
- **Dataset**: `fct_daily_stock_metrics`
- **X-Axis**: `ticker`
- **Metrics**: `SUM(volume)`
- **Description**: Compares liquidity and total trading activity across tickers.

### Chart 4: Top Daily Returns & Volatility (Table View)
- **Chart Type**: Table
- **Dataset**: `fct_daily_stock_metrics`
- **Columns**: `stock_date`, `ticker`, `close_price`, `daily_return_pct`, `volatility_7d`
- **Sort By**: `stock_date` (DESC)
- **Description**: Financial tabular view for quantitative analysis.

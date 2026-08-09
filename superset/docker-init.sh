#!/usr/bin/env bash
set -e

echo "=== Initializing Apache Superset for MarketVault ==="

# Upgrade Superset Metadata DB
superset db upgrade || true

# Create Admin User
superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@marketvault.com \
  --password admin || true

# Initialize default roles and permissions
superset init || true

# Automatically register MarketVault PostgreSQL database connection & datasets
python3 -c "
try:
    from superset.app import create_app
    app = create_app()
    with app.app_context():
        from superset import db
        from superset.models.core import Database
        from superset.connectors.sqla.models import SqlaTable

        database = db.session.query(Database).filter_by(database_name='MarketVault StockDB').first()
        if not database:
            database = Database(
                database_name='MarketVault StockDB',
                sqlalchemy_uri='postgresql+psycopg2://airflow:airflow@postgres:5432/stockdb'
            )
            db.session.add(database)
            db.session.commit()
            print('Successfully registered MarketVault StockDB database connection!')

        tbl_fact = db.session.query(SqlaTable).filter_by(table_name='fct_daily_stock_metrics', database_id=database.id).first()
        if not tbl_fact:
            tbl_fact = SqlaTable(table_name='fct_daily_stock_metrics', schema='public', database_id=database.id)
            db.session.add(tbl_fact)
            db.session.commit()
            tbl_fact.fetch_metadata()
            print('Successfully registered fct_daily_stock_metrics dataset!')

        tbl_stg = db.session.query(SqlaTable).filter_by(table_name='stg_stock_prices', database_id=database.id).first()
        if not tbl_stg:
            tbl_stg = SqlaTable(table_name='stg_stock_prices', schema='public', database_id=database.id)
            db.session.add(tbl_stg)
            db.session.commit()
            tbl_stg.fetch_metadata()
            print('Successfully registered stg_stock_prices dataset!')

except Exception as err:
    print('Note regarding auto db/dataset registration:', err)
" || true

echo "=== Starting Apache Superset Server on port 8088 ==="
exec gunicorn \
  --bind 0.0.0.0:8088 \
  --workers 2 \
  --timeout 120 \
  --limit-request-line 0 \
  --limit-request-field_size 0 \
  "superset.app:create_app()"

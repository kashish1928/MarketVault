# MarketVault

MarketVault is a modern data engineering pipeline infrastructure for ingesting, transforming, and analyzing stock market data.

## Project Structure

```
MarketVault/
├── airflow/
│   ├── dags/          # Airflow DAG definitions (e.g. stock ingestion)
│   ├── logs/          # Airflow execution logs
│   └── plugins/       # Custom Airflow plugins
├── dbt/               # dbt data transformation models & profiles
├── postgres/          # PostgreSQL scripts & database testing scripts
├── docker/            # Custom Dockerfiles (Airflow 3, dbt)
├── .github/           # GitHub Actions workflows
├── docker-compose.yaml # Container orchestration setup
├── .env               # Environment variables configuration
├── makefile           # Quick command shortcuts
├── requirements.txt   # Python dependencies
├── README.md
└── LICENSE
```

## Prerequisites

- **macOS / Linux**
- **Colima** (Container runtime for macOS) & **Docker CLI** / `docker compose`
- **Python 3.9+** (optional, for local virtual environment)
- **Make** (optional, for convenience commands)

---

## Environment Setup

1. **Configure Environment Variables**:
   Ensure you have a `.env` file in the root directory with the following variables:
   ```env
   AIRFLOW_UID=501
   POSTGRES_DB=stockdb
   ```
   *(Note: On Linux systems, you can set `AIRFLOW_UID=$(id -u)`).*

2. *(Optional)* **Set up Local Python Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   make init
   ```

---

## Running the Application (Colima & Docker)

### 1. Start Colima Container Runtime
Before starting any containers, start the Colima VM:
```bash
colima start
```
*(Recommended resource allocation for Airflow 3 & Postgres: `colima start --cpu 4 --memory 8`)*

### 2. Build & Launch Containers
Build the custom Airflow Docker image (which packages `requirements.txt`) and start all container services in detached mode:

**Using Makefile:**
```bash
make build
```
**Using Docker Compose directly:**
```bash
docker compose -f docker-compose.yaml up --build -d
```

### 3. Verify Container Status
Check that all containers are running and healthy:
```bash
docker compose ps
```

---

## Services Architecture (Ready Services)

| Service | Container Name | Host Port / Access | Description |
| :--- | :--- | :--- | :--- |
| **PostgreSQL** | `postgres` | `localhost:5433` | Primary database (`stockdb`) & Airflow metadata backend |
| **Redis** | `redis` | Internal `6379` | Celery message broker |
| **Airflow Init** | `airflow-init` | N/A | One-time DB migration & admin user creation (`airflow`/`airflow`) |
| **Airflow Web UI / API** | `airflow-apiserver` | `http://localhost:8080` | Airflow 3 Web interface and API server |
| **Airflow Scheduler** | `airflow-scheduler` | N/A | Schedules DAG executions |
| **Airflow DAG Processor** | `airflow-dag-processor` | N/A | Parses DAG files from `./airflow/dags` |
| **Airflow Worker** | `airflow-worker` | N/A | Celery worker executing tasks |
| **Airflow Triggerer** | `airflow-triggerer` | N/A | Handles deferred & async tasks |

---

## Accessing Services & Testing

### 1. Airflow Web UI
- **URL**: [http://localhost:8080](http://localhost:8080)
- **Default Credentials**:
  - **Username**: `airflow`
  - **Password**: `airflow`

### 2. PostgreSQL Connection & Testing
- **Connect via CLI**:
  ```bash
  make psql
  ```
- **Test Database Read/Write**:
  ```bash
  python postgres/test_postgres.py
  ```

### 3. Monitoring Logs
Stream live container logs:
```bash
make logs
# OR
docker compose -f docker-compose.yaml logs -f
```

---

## Stopping & Restarting Services

- **Start existing containers** (without rebuilding):
  ```bash
  make up
  ```
- **Restart all containers**:
  ```bash
  make restart
  ```
- **Stop containers**:
  ```bash
  make down
  ```
- **Stop Colima VM**:
  ```bash
  colima stop
  ```

---

## Makefile Command Summary

| Command | Action |
| :--- | :--- |
| `make init` | Install Python dependencies from `requirements.txt` |
| `make activate` | Activate virtual environment |
| `make build` | Rebuild images and start container stack (`docker compose up --build -d`) |
| `make up` | Start existing containers in background |
| `make down` | Stop and remove running containers |
| `make restart` | Restart all container services |
| `make logs` | Stream live container logs |
| `make psql` | Connect to PostgreSQL database CLI (`stockdb`) on `localhost:5433` |

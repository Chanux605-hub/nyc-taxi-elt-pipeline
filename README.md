# NYC Taxi ELT Pipeline

An end-to-end, cloud-native ELT pipeline that ingests 2.9M+ NYC Yellow Taxi trip records, transforms them through a medallion architecture, and delivers business insights via an interactive dashboard — fully orchestrated and automatically tested on every code push.

---

## Architecture

```
NYC TLC Open Data (Parquet)
         |
         v
Python Ingestion Script
(load_raw.py)
         |
         v
Snowflake — RAW Schema
(unmodified source data)
         |
         v
dbt Core Transformations
  Staging  →  Intermediate  →  Marts
(clean)      (join zones)    (reporting tables)
         |
         v
Metabase Dashboard
(revenue, trip volume, zone analytics)

Airflow DAG orchestrates all steps daily at midnight
GitHub Actions runs dbt tests on every pull request
```

---

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Ingestion | Python + Snowflake Connector | Load raw Parquet files into Snowflake |
| Warehouse | Snowflake | Cloud data warehouse |
| Transformation | dbt Core | SQL models, testing, documentation |
| Orchestration | Apache Airflow | Schedule and automate the pipeline |
| Containerisation | Docker | Run Airflow locally via Docker Compose |
| Dashboard | Metabase | Business intelligence and visualisation |
| CI/CD | GitHub Actions | Automated dbt testing on every push |

---

## What the Pipeline Does

**Extract & Load** — A Python script reads NYC TLC Yellow Taxi Parquet files and loads them into Snowflake's RAW schema using chunked inserts. A zone lookup CSV is loaded as a dimension table.

**Transform** — dbt Core transforms raw data through three layers:
- `staging` — cleans column names, casts data types, filters invalid trips (zero distance, negative fares), and deduplicates records using ROW_NUMBER() window functions
- `intermediate` — joins trip data to the taxi zone lookup table, replacing numeric location IDs with real zone and borough names
- `marts` — builds final reporting tables (`fct_trips`, `dim_zones`) with surrogate keys, calculated trip duration, and 18 automated data quality tests

**Orchestrate** — An Airflow DAG runs the full pipeline daily at midnight in three sequential tasks: ingest data → run dbt models → run dbt tests. If any task fails, downstream tasks are skipped automatically.

**Serve** — Metabase connects to Snowflake mart tables and displays four charts: trip volume by week, revenue by borough, average fare by payment type, and top pickup zones.

---

## Key Results (January 2024)

- **2.9M+** taxi trips processed
- **$1.49M** total revenue across NYC boroughs
- **Queens** accounts for 64% of revenue (driven by JFK Airport trips)
- **18 dbt tests** passing — not_null, unique, accepted_values across all models
- Full pipeline runs automatically every day with zero manual steps

---

## Project Structure

```
nyc-taxi-elt-pipeline/
├── airflow/
│   └── dags/
│       └── taxi_pipeline_dag.py    # Airflow DAG definition
├── dbt/
│   └── taxi_pipeline/
│       └── models/
│           ├── staging/            # stg_yellow_trips, stg_taxi_zones
│           ├── intermediate/       # int_trips_with_zones
│           └── marts/              # fct_trips, dim_zones
├── scripts/
│   ├── load_raw.py                 # Python ingestion script
│   ├── download_data.py            # Downloads TLC Parquet files
│   └── inspect_data.py            # Data profiling utility
├── .github/
│   └── workflows/
│       └── dbt_ci.yml              # GitHub Actions CI/CD workflow
├── Dockerfile                      # Custom Airflow image with dbt
├── docker-compose.yml              # Airflow + Metabase services
└── .env                            # Snowflake credentials (not committed)
```

---

## Data Model

```
taxi_db/
├── raw/
│   ├── yellow_trips        # Raw trip data as loaded from TLC
│   └── taxi_zones          # Zone lookup table (265 NYC zones)
├── staging/
│   ├── stg_yellow_trips    # Cleaned, deduplicated trips
│   └── stg_taxi_zones      # Cleaned zone reference data
└── marts/
    ├── fct_trips           # Final fact table with zone names and trip duration
    └── dim_zones           # Final dimension table of all NYC taxi zones
```

---

## CI/CD

Every pull request that touches `dbt/` files automatically triggers a GitHub Actions workflow that:
1. Installs Python 3.11 and dbt-snowflake on a fresh Ubuntu runner
2. Creates `profiles.yml` from GitHub Secrets (no credentials in code)
3. Runs `dbt deps`, `dbt run`, and `dbt test`
4. Reports pass or fail directly on the pull request

---

## How to Run Locally

**Prerequisites:** Python 3.11, Docker Desktop, Git

```bash
# 1. Clone the repo
git clone https://github.com/Chanux605-hub/nyc-taxi-elt-pipeline.git
cd nyc-taxi-elt-pipeline

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install pandas pyarrow snowflake-connector-python python-dotenv dbt-snowflake

# 4. Configure credentials
# Fill in .env with your Snowflake account details
# Create ~/.dbt/profiles.yml with Snowflake connection

# 5. Download dataset
python scripts/download_data.py

# 6. Load raw data into Snowflake
python scripts/load_raw.py

# 7. Run dbt transformations
cd dbt/taxi_pipeline
dbt deps
dbt run
dbt test

# 8. Start Airflow and Metabase
cd ../..
docker-compose up -d
# Airflow UI: http://localhost:8080 (admin/admin)
# Metabase:   http://localhost:3000
```

---

## Author

**Budeesha Chanuka**
Data Engineering Undergraduate — SLIIT
GitHub: [Chanux605-hub](https://github.com/Chanux605-hub)
LinkedIn: [linkedin.com/in/budeesha-chanuka](https://linkedin.com/in/budeesha-chanuka)

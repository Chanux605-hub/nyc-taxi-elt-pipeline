# NYC Taxi ELT Pipeline

End-to-end ELT pipeline using Airbyte, Snowflake, dbt, and Airflow.

## Architecture
Source (NYC TLC Parquet) → Airbyte → Snowflake RAW → dbt Staging → dbt Marts → Metabase

## Stack
- **Ingestion**: Airbyte
- **Warehouse**: Snowflake
- **Transformation**: dbt Core
- **Orchestration**: Apache Airflow
- **BI**: Metabase

## Setup
See the phase guides in `/docs` for step-by-step setup instructions.

## Project Structure
```
nyc-taxi-elt-pipeline/
├── airflow/          # Airflow DAGs and config
├── dbt/              # dbt project (transformations)
├── data/raw/         # Local raw parquet files (not committed)
├── scripts/          # Utility scripts (inspect, upload)
└── .github/workflows # CI/CD workflows
```

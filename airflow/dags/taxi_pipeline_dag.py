# ============================================================
# Section 1 — Imports
# Bring in the libraries needed to build the DAG
# ============================================================
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator


# ============================================================
# Section 2 — Default Arguments
# Settings that apply to every task in this DAG
# retries=1 means if a task fails, try once more after 5 mins
# ============================================================
default_args = {
    'owner': 'chanuka',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


# ============================================================
# Section 3 — DAG Definition
# Name, schedule, and start date of the pipeline
# schedule_interval: '0 0 * * *' = every day at midnight
# catchup=False means don't run for past dates
# ============================================================
dag = DAG(
    'taxi_pipeline',
    default_args=default_args,
    description='NYC Taxi ELT Pipeline',
    schedule_interval='0 0 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['nyc', 'taxi', 'elt'],
)


# ============================================================
# Section 4 — Tasks
# Each task is one step in the pipeline
# BashOperator runs a shell command inside the Docker container
# /opt/airflow/project = your project folder mapped into Docker
# ============================================================

# Task 1: Run the Python ingestion script
# Loads parquet files from data/raw/ into Snowflake RAW schema
ingest_data = BashOperator(
    task_id='ingest_data',
    bash_command='cd /opt/airflow/project && python -u scripts/load_raw.py',
    dag=dag,
)

# Task 2: Run dbt models
# Transforms RAW → staging → intermediate → marts in Snowflake
dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command='cd /opt/airflow/project/dbt/taxi_pipeline && dbt run --profiles-dir /opt/airflow/project/dbt/taxi_pipeline',
    dag=dag,
)

# Task 3: Run dbt tests
# Runs all 18 data quality tests to verify the pipeline output
dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command='cd /opt/airflow/project/dbt/taxi_pipeline && dbt test --profiles-dir /opt/airflow/project/dbt/taxi_pipeline',
    dag=dag,
)


# ============================================================
# Section 5 — Task Dependencies
# Defines the execution order using >> operator
# ingest first → then transform → then test
# If any task fails, everything after it is skipped
# ============================================================
ingest_data >> dbt_run >> dbt_test
import os
import subprocess

PROJECT_NAME = "nyc-taxi-elt-pipeline"
BASE = os.getcwd()

folders = [
    "airflow/dags",
    "airflow/plugins",
    "airflow/logs",
    "dbt",
    "data/raw",
    "scripts",
    ".github/workflows",
]

for folder in folders:
    os.makedirs(os.path.join(BASE, folder), exist_ok=True)
    print(f"  created  {folder}/")

files = {
    ".gitignore": """\
# Environment & secrets
.env
*.env

# Data files (too large for git)
data/
*.parquet
*.csv
*.json

# Python
__pycache__/
*.pyc
.venv/
venv/

# dbt
dbt/taxi_pipeline/target/
dbt/taxi_pipeline/dbt_packages/
dbt/taxi_pipeline/logs/

# Airflow
airflow/logs/
airflow/plugins/__pycache__/

# OS
.DS_Store
""",

    ".env": """\
# Snowflake credentials - fill these in
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=pipeline_user
SNOWFLAKE_PASSWORD=YourStrongPassword123!
SNOWFLAKE_DATABASE=taxi_db
SNOWFLAKE_WAREHOUSE=taxi_wh
SNOWFLAKE_SCHEMA=raw

# Airflow
AIRFLOW_UID=50000
""",

    "README.md": """\
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
""",

    "scripts/inspect_data.py": """\
import pandas as pd
import sys
import os

def inspect(path: str):
    print(f"\\n=== Inspecting: {path} ===")
    if path.endswith(".parquet"):
        df = pd.read_parquet(path)
    elif path.endswith(".csv"):
        df = pd.read_csv(path)
    else:
        print("Unsupported file type. Use .parquet or .csv")
        return

    print(f"Shape         : {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"\\nColumn types:\\n{df.dtypes.to_string()}")
    print(f"\\nNull counts:\\n{df.isnull().sum().to_string()}")
    print(f"\\nSample (3 rows):\\n{df.head(3).to_string()}")
    print(f"\\nNumeric summary:\\n{df.describe().to_string()}")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path:
        raw_dir = os.path.join(os.path.dirname(__file__), "../data/raw")
        files = [f for f in os.listdir(raw_dir) if f.endswith((".parquet", ".csv"))]
        if not files:
            print("No files found in data/raw/. Download the TLC parquet files first.")
            sys.exit(1)
        for f in sorted(files):
            inspect(os.path.join(raw_dir, f))
    else:
        inspect(path)
""",

    "scripts/download_data.py": """\
import urllib.request
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../data/raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 3 months of Yellow Taxi data + Zone lookup
FILES = [
    ("https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet", "yellow_tripdata_2024-01.parquet"),
    ("https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-02.parquet", "yellow_tripdata_2024-02.parquet"),
    ("https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-03.parquet", "yellow_tripdata_2024-03.parquet"),
    ("https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv",                 "taxi_zone_lookup.csv"),
]

def download(url, filename):
    dest = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(dest):
        print(f"  already exists: {filename}")
        return
    print(f"  downloading: {filename} ...")
    urllib.request.urlretrieve(url, dest)
    size_mb = os.path.getsize(dest) / 1_000_000
    print(f"  done: {filename} ({size_mb:.1f} MB)")

if __name__ == "__main__":
    print("Downloading NYC TLC datasets...")
    for url, name in FILES:
        download(url, name)
    print("\\nAll files saved to data/raw/")
""",

    ".github/workflows/dbt_ci.yml": """\
name: dbt CI

on:
  pull_request:
    paths:
      - 'dbt/**'

jobs:
  dbt-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dbt
        run: pip install dbt-snowflake
      - name: Run dbt tests
        env:
          SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
          SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
          SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
        run: |
          cd dbt/taxi_pipeline
          dbt deps
          dbt test
""",
}

for filename, content in files.items():
    full_path = os.path.join(BASE, filename)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  created  {filename}")

print(f"\nProject scaffolded at: {BASE}")
print("\nNext steps:")
print("  1. cd", PROJECT_NAME)
print("  2. git init && git add . && git commit -m 'initial scaffold'")
print("  3. python scripts/download_data.py")
print("  4. python scripts/inspect_data.py")

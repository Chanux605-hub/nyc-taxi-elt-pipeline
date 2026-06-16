import os
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

def get_snowflake_connection():
    conn = snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )
    conn.cursor().execute("USE WAREHOUSE taxi_wh")
    return conn

def create_raw_tables(cursor):
    cursor.execute("""
        create table if not exists taxi_db.raw.yellow_trips (
            VendorID              NUMBER,
            tpep_pickup_datetime  TIMESTAMP,
            tpep_dropoff_datetime TIMESTAMP,
            passenger_count       NUMBER,
            trip_distance         FLOAT,
            RatecodeID            NUMBER,
            store_and_fwd_flag    VARCHAR,
            PULocationID          NUMBER,
            DOLocationID          NUMBER,
            payment_type          NUMBER,
            fare_amount           FLOAT,
            extra                 FLOAT,
            mta_tax               FLOAT,
            tip_amount            FLOAT,
            tolls_amount          FLOAT,
            improvement_surcharge FLOAT,
            total_amount          FLOAT,
            congestion_surcharge  FLOAT,
            Airport_fee           FLOAT
        )
    """)

    cursor.execute("""
        create table if not exists taxi_db.raw.taxi_zones (
            LocationID NUMBER,
            Borough    VARCHAR,
            Zone       VARCHAR,
            service_zone VARCHAR
        )
    """)

    cursor.execute("TRUNCATE TABLE IF EXISTS taxi_db.raw.yellow_trips")
    cursor.execute("TRUNCATE TABLE IF EXISTS taxi_db.raw.taxi_zones")
    print("Tables truncated - ready for fresh load.")

    print("Raw tables created successfully.")

def load_yellow_trips(cursor):
    raw_dir = os.path.join(os.path.dirname(__file__), "../data/raw")

    files = [
        "yellow_tripdata_2024-01.parquet",
        "yellow_tripdata_2024-02.parquet",
        "yellow_tripdata_2024-03.parquet"
    ]

    for file in files:
        file_path = os.path.join(raw_dir, file)
        print(f"Loading {file}...")

        df = pd.read_parquet(file_path)

        df.columns = [col.upper() for col in df.columns]

        for col in df.select_dtypes(include=["datetimetz", "datetime64"]).columns:
            df[col] = df[col].astype(str)

        df = df.where(pd.notnull(df), None)
        df = df.replace({float('nan'): None, 'nan': None, 'NaT': None})

        data = [tuple(row) for row in df.itertuples(index=False)]

        chunk_size = 1000
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            placeholders = ",".join(["(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"] * len(chunk))
            flat_data = [val for row in chunk for val in row]
            cursor.execute(f"INSERT INTO taxi_db.raw.yellow_trips VALUES {placeholders}", flat_data)
            if i % 100000 == 0:
                print(f"  inserted {i:,} rows so far...")

        print(f"Done: {file} - {len(df):,} rows inserted.")

def load_taxi_zones(cursor):
    raw_dir = os.path.join(os.path.dirname(__file__), "../data/raw")
    file_path = os.path.join(raw_dir, "taxi_zone_lookup.csv")

    print("Loading taxi zones...")

    df =  pd.read_csv(file_path)

    df.columns = [col.upper() for col in df.columns]

    for col in df.select_dtypes(include=["datetimetz", "datetime64"]).columns:
        df[col] = df[col].astype(str)

    df = df.where(pd.notnull(df), None)
    df = df.replace({float('nan'): None, 'nan': None, 'NaT': None})

    data = [tuple(row) for row in df.itertuples(index=False)]

    cursor.executemany("""
        insert into taxi_db.raw.taxi_zones values(
                       %s, %s, %s, %s
        )
    """, data)

    print(f"Done: taxi_zones - {len(df):,} rows inserted.")

def main():
    print("Connecting to Snowflake...")
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        create_raw_tables(cursor)
        load_yellow_trips(cursor)
        load_taxi_zones(cursor)
        print("All data loaded successfully!")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        cursor.close()
        conn.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
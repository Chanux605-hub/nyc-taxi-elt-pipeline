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
    print("\nAll files saved to data/raw/")

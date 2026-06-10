import pandas as pd
import sys
import os

def inspect(path: str):
    print(f"\n=== Inspecting: {path} ===")
    if path.endswith(".parquet"):
        df = pd.read_parquet(path)
    elif path.endswith(".csv"):
        df = pd.read_csv(path)
    else:
        print("Unsupported file type. Use .parquet or .csv")
        return

    print(f"Shape         : {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"\nColumn types:\n{df.dtypes.to_string()}")
    print(f"\nNull counts:\n{df.isnull().sum().to_string()}")
    print(f"\nSample (3 rows):\n{df.head(3).to_string()}")
    print(f"\nNumeric summary:\n{df.describe().to_string()}")

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

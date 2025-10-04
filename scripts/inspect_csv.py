"""
Inspect the Enron CSV structure.
"""
import pandas as pd
from src.config import RAW_DATA_DIR

# Load first 5 rows
df = pd.read_csv(RAW_DATA_DIR / "emails.csv", nrows=5)

print("CSV Columns:")
print(df.columns.tolist())
print("\n" + "="*60)

print("\nFirst email sample:")
print("="*60)
print(df.iloc[0]['message'][:1000])  # First 1000 chars
print("\n" + "="*60)

print("\nDataFrame Info:")
print(df.info())
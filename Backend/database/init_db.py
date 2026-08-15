import sqlite3
import pandas as pd

DB_PATH = "database/data.db"
CSV_PATH = "database/dataset/train.csv"

# Read CSV
df = pd.read_csv(CSV_PATH)

# Normalize column names
df.columns = (
    df.columns
        .str.strip()          # Remove leading/trailing spaces
        .str.lower()          # Lowercase
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
)

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)

# Write DataFrame to SQLite
df.to_sql(
    "sales",
    conn,
    if_exists="replace",
    index=False
)

conn.commit()
conn.close()

print("Database created successfully!")
print("Columns:")
print(df.columns.tolist())
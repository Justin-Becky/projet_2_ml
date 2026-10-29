import pandas as pd


df = pd.read_parquet("../donnees/2026-06-21_0.parquet")

print(df.head())
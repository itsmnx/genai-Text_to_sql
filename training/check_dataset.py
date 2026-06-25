import pandas as pd

df = pd.read_csv("data/train.csv")

print(df.head())
print()
print(df.columns)
print()
print("Rows:", len(df))
import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("data/train.csv")

train_df, temp_df = train_test_split(
    df,
    test_size=0.2,
    random_state=42
)

val_df, test_df = train_test_split(
    temp_df,
    test_size=0.5,
    random_state=42
)

train_df.to_csv("data/train_split.csv", index=False)
val_df.to_csv("data/validation.csv", index=False)
test_df.to_csv("data/test.csv", index=False)

print("Done")
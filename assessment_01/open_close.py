import pandas as pd
import numpy as np

df = pd.read_csv('data.csv')

columns = df.columns.tolist()
print("Columns:", columns)

for open_col in columns:
    for close_col in columns:
        if open_col == close_col:
            continue

        print(f"\nSelected columns: open = '{open_col}', close = '{close_col}'")

        df['prev_close'] = df[close_col].shift(1)

        df['abs_diff'] = (df[open_col] - df['prev_close']).abs()

        diffs = df['abs_diff'].dropna()

        print(f"Sum of differences: {diffs.sum()}")

# flux and pulse have the lowest diffsd
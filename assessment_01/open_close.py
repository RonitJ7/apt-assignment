import pandas as pd
import numpy as np

df = pd.read_csv('data.csv')

df.columns = df.columns.str.strip()
columns = df.columns.tolist()

print("Columns:", columns)

df_prev = df.shift(1)

results = []

for open_col in columns:
    for close_col in columns:
        if open_col == close_col or (open_col == 'neutronCount') or (close_col == 'neutronCount'):
            continue
        
        diff_sum = abs(df[open_col].iloc[1:] - df_prev[close_col].iloc[1:]).sum()
        
        results.append((open_col, close_col, diff_sum))
        print(f"{open_col}, {close_col}, {diff_sum}")

# Find the minimum difference
min_result = min(results, key=lambda x: x[2])
print(f"\nLowest difference: {min_result[0]} (open) vs {min_result[1]} (close) = {min_result[2]}")

# Show top 5 lowest differences for better analysis
sorted_results = sorted(results, key=lambda x: x[2])
for i, (open_col, close_col, diff) in enumerate(sorted_results[:]):
    print(f"{i+1}. {open_col} (open) vs {close_col} (close) = {diff}")
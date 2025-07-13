import pandas as pd
import numpy as np

df = pd.read_csv('data.csv')

columns = df.columns.tolist()
print("Columns:", columns)

filtered_columns = [col for col in columns if col != 'neutronCount']

for high_col in filtered_columns:
    for low_col in filtered_columns:
        if high_col == low_col:
            continue
            
        if (df[high_col] >= df[low_col]).all():
            print(f"{high_col}, {low_col} satisfy the high low conditions")
        else:
            print(f"{high_col}, {low_col} tested")
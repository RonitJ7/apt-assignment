import pandas as pd
import numpy as np

df = pd.read_csv('data_smoothed.csv')

df.columns = df.columns.str.strip()
columns = df.columns.tolist()

print("Columns:", columns)

df_prev = df.shift(1)

results = []

for open_col in ['deltaX', 'flux', 'pulse']:
    for close_col in ['deltaX', 'flux', 'pulse']:
        if open_col == close_col:        
            continue

        price_col = ['deltaX', 'flux', 'pulse'].copy()
        price_col.remove(open_col)
        price_col.remove(close_col)
        price_col = price_col[0]

        closecount = 0
        opencount = 0
        
        open_distance = abs(df[price_col] - df_prev[open_col])
        close_distance = abs(df[price_col] - df_prev[close_col])
            
        closer_to_open = (open_distance < close_distance).sum()
        closer_to_close = (close_distance < open_distance).sum()
            
        opencount += closer_to_open
        closecount += closer_to_close
        
        print(f"\nOpen: {open_col}, Close: {close_col}, Price: {price_col}")
        print(f"Closer to Open: {opencount}")
        print(f"Closer to Close: {closecount}")
        print(f"Open % (lower the better): {100* opencount / (opencount + closecount):.2f}")
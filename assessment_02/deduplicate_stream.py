import pandas as pd
import sys
import argparse

def deduplicate_data(df, strategy='latest', window='200ms'):
    print(f"Input records: {len(df)}")

    if df['timestamp'].dtype == 'object':
        print("Converting timestamps...")
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601', utc=True, errors='coerce')
    n_bad = df['timestamp'].isna().sum()
    if n_bad > 0:
        print(f"WARNING: {n_bad} timestamps could not be parsed and will be dropped.")
        failed_timestamps = df[df['timestamp'].isna()]['timestamp'].head(5)
        print("Sample failed timestamps:", failed_timestamps.tolist())
        df = df.dropna(subset=['timestamp']).reset_index(drop=True)
    print(f"Records after timestamp parsing: {len(df)}")

    df.loc[:, 'timestamp_rounded'] = df['timestamp'].dt.round(window)

    if strategy == 'latest':
        deduped = df.sort_values('timestamp').drop_duplicates(subset=['symbol', 'timestamp_rounded'], keep='last')
    elif strategy == 'first':
        deduped = df.sort_values('timestamp').drop_duplicates(subset=['symbol', 'timestamp_rounded'], keep='first')
    elif strategy == 'average':
        deduped = df.groupby(['symbol', 'timestamp_rounded'], as_index=False)['price'].mean()
    elif strategy == 'highest_price':
        idx = df.groupby(['symbol', 'timestamp_rounded'])['price'].idxmax()
        deduped = df.loc[idx].reset_index(drop=True)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    deduped = deduped.sort_values(['symbol', 'timestamp_rounded', 'timestamp']).reset_index(drop=True)
    deduped = deduped.rename(columns={'timestamp_rounded': 'timestamp'})
    deduped = deduped[['symbol', 'timestamp', 'price']]

    print(f"Output records: {len(deduped)}")
    print(f"Removed {len(df) - len(deduped)} duplicate records (window: {window})")
    return deduped

def main():
    parser = argparse.ArgumentParser(description='Deduplicate stream processing output (windowed deduplication)')
    parser.add_argument('input_file', help='Input CSV file')
    parser.add_argument('output_file', help='Output CSV file')
    parser.add_argument('--strategy', choices=['latest', 'first', 'average', 'highest_price'], default='latest')
    parser.add_argument('--window', type=str, default='200ms', help='Deduplication window (e.g., 200ms, 1s)')
    args = parser.parse_args()

    try:
        print(f"Loading data from {args.input_file}...")
        df = pd.read_csv(args.input_file)
        print(f"Loaded {len(df)} records")
        required_columns = ['symbol', 'timestamp', 'price']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Error: Missing required columns: {missing_columns}")
            sys.exit(1)
        deduped_df = deduplicate_data(df, args.strategy, window=args.window)
        deduped_df.to_csv(args.output_file, index=False)
        print(f"Deduplicated data saved to {args.output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

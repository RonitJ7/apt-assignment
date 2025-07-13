import pandas as pd
import sys
import argparse

def deduplicate_data(df, strategy='latest', window='200ms'):
    print(f"Input records: {len(df)}")

    # Parse timestamps robustly
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

    # Round timestamps to the nearest window (e.g., 200ms)
    df.loc[:, 'timestamp_200ms'] = df['timestamp'].dt.round(window)

    # Deduplicate based on symbol and rounded timestamp
    if strategy == 'latest':
        deduped = df.sort_values('timestamp').drop_duplicates(subset=['symbol', 'timestamp_200ms'], keep='last')
    elif strategy == 'first':
        deduped = df.sort_values('timestamp').drop_duplicates(subset=['symbol', 'timestamp_200ms'], keep='first')
    elif strategy == 'average':
        deduped = df.groupby(['symbol', 'timestamp_200ms'], as_index=False)['price'].mean()
    elif strategy == 'highest_price':
        idx = df.groupby(['symbol', 'timestamp_200ms'])['price'].idxmax()
        deduped = df.loc[idx].reset_index(drop=True)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    # Sort and clean up
    deduped = deduped.sort_values(['symbol', 'timestamp_200ms', 'timestamp']).reset_index(drop=True)
    deduped = deduped.rename(columns={'timestamp_200ms': 'timestamp'})
    deduped = deduped[['symbol', 'timestamp', 'price']]

    print(f"Output records: {len(deduped)}")
    print(f"Removed {len(df) - len(deduped)} duplicate records (window: {window})")
    return deduped

def main():
    parser = argparse.ArgumentParser(description='Deduplicate stream processing output (200ms window)')
    parser.add_argument('input_file', help='Input CSV file')
    parser.add_argument('output_file', help='Output CSV file')
    parser.add_argument('--strategy', choices=['latest', 'first', 'average', 'highest_price'], default='latest')
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
        deduped_df = deduplicate_data(df, args.strategy, window='200ms')
        deduped_df.to_csv(args.output_file, index=False)
        print(f"Deduplicated data saved to {args.output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

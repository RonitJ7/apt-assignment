import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def is_monotonic_sequence_all_cols(df_subset, direction, tolerance, columns_to_analyze):
    """
    Check if ALL columns in a subsequence are monotonic in the given direction with tolerance.
    
    Args:
        df_subset: pandas DataFrame subset to check
        direction: 'increasing' or 'decreasing'
        tolerance: Maximum allowed counter-movement
        columns_to_analyze: List of columns to check
    
    Returns:
        Boolean indicating if ALL columns are monotonic in the given direction
    """
    if len(df_subset) < 2:
        return False
    
    # Check each column
    for column in columns_to_analyze:
        if df_subset[column].dtype not in ['int64', 'float64']:
            continue
            
        subsequence = df_subset[column]
        
        if direction == 'increasing':
            # Check if overall trend is increasing
            if subsequence.iloc[-1] <= subsequence.iloc[0]:
                return False
            
            # Check that no point decreases by more than tolerance
            for i in range(1, len(subsequence)):
                decrease = subsequence.iloc[i-1] - subsequence.iloc[i]
                if decrease > tolerance:
                    return False
                    
        elif direction == 'decreasing':
            # Check if overall trend is decreasing
            if subsequence.iloc[-1] >= subsequence.iloc[0]:
                return False
            
            # Check that no point increases by more than tolerance
            for i in range(1, len(subsequence)):
                increase = subsequence.iloc[i] - subsequence.iloc[i-1]
                if increase > tolerance:
                    return False
    
    return True

def find_monotonic_intervals_all_cols(df, tolerance=0.05, columns_to_analyze=None):
    """
    Find monotonic intervals where ALL columns consistently go in the same direction.
    
    Args:
        df: pandas DataFrame to analyze
        tolerance: Maximum allowed counter-movement (default: 0.05)
        columns_to_analyze: List of column names to analyze (default: first 5 columns)
    
    Returns:
        List of dictionaries containing interval information
    """
    if columns_to_analyze is None:
        columns_to_analyze = df.columns[:5]
    
    if len(df) < 2:
        return []
    
    intervals = []
    start_idx = 0
    
    while start_idx < len(df) - 1:
        # Try to find the longest monotonic sequence starting from start_idx
        best_interval = None
        
        # Check for increasing sequences
        for end_idx in range(start_idx + 1, len(df)):
            df_subset = df.iloc[start_idx:end_idx + 1]
            if is_monotonic_sequence_all_cols(df_subset, 'increasing', tolerance, columns_to_analyze):
                # Calculate aggregate statistics
                start_values = {col: df[col].iloc[start_idx] for col in columns_to_analyze if df[col].dtype in ['int64', 'float64']}
                end_values = {col: df[col].iloc[end_idx] for col in columns_to_analyze if df[col].dtype in ['int64', 'float64']}
                changes = {col: end_values[col] - start_values[col] for col in start_values.keys()}
                
                best_interval = {
                    'start': start_idx,
                    'end': end_idx,
                    'type': 'increasing',
                    'length': end_idx - start_idx,
                    'start_values': start_values,
                    'end_values': end_values,
                    'changes': changes,
                    'total_change': sum(changes.values())
                }
            else:
                break
        
        # Check for decreasing sequences (only if no increasing sequence found)
        if best_interval is None:
            for end_idx in range(start_idx + 1, len(df)):
                df_subset = df.iloc[start_idx:end_idx + 1]
                if is_monotonic_sequence_all_cols(df_subset, 'decreasing', tolerance, columns_to_analyze):
                    # Calculate aggregate statistics
                    start_values = {col: df[col].iloc[start_idx] for col in columns_to_analyze if df[col].dtype in ['int64', 'float64']}
                    end_values = {col: df[col].iloc[end_idx] for col in columns_to_analyze if df[col].dtype in ['int64', 'float64']}
                    changes = {col: end_values[col] - start_values[col] for col in start_values.keys()}
                    
                    best_interval = {
                        'start': start_idx,
                        'end': end_idx,
                        'type': 'decreasing',
                        'length': end_idx - start_idx,
                        'start_values': start_values,
                        'end_values': end_values,
                        'changes': changes,
                        'total_change': sum(changes.values())
                    }
                else:
                    break
        
        if best_interval and best_interval['length'] >= 2:  # Minimum length of 2
            intervals.append(best_interval)
            start_idx = best_interval['end']
        else:
            start_idx += 1
    
    return intervals

def merge_adjacent_intervals(intervals):
    """
    Merge adjacent intervals of the same type.
    
    Args:
        intervals: List of interval dictionaries
    
    Returns:
        List of merged interval dictionaries
    """
    if not intervals:
        return []
    
    merged = []
    current_interval = intervals[0].copy()
    
    for i in range(1, len(intervals)):
        next_interval = intervals[i]
        
        # Check if intervals are adjacent and of the same type
        if (current_interval['end'] == next_interval['start'] and 
            current_interval['type'] == next_interval['type']):
            
            # Merge intervals
            current_interval['end'] = next_interval['end']
            current_interval['length'] += next_interval['length']
            current_interval['end_values'] = next_interval['end_values']
            
            # Recalculate changes
            current_interval['changes'] = {
                col: current_interval['end_values'][col] - current_interval['start_values'][col] 
                for col in current_interval['start_values'].keys()
            }
            current_interval['total_change'] = sum(current_interval['changes'].values())
        else:
            # Save current interval and start new one
            merged.append(current_interval)
            current_interval = next_interval.copy()
    
    # Add the last interval
    merged.append(current_interval)
    
    return merged

def count_tolerance_violations_all_cols(df_subset, direction, tolerance, columns_to_analyze):
    """
    Count how many points violate the tolerance across all columns.
    
    Args:
        df_subset: pandas DataFrame subset
        direction: 'increasing' or 'decreasing'
        tolerance: Maximum allowed counter-movement
        columns_to_analyze: List of columns to check
    
    Returns:
        Dictionary with violation counts per column
    """
    violations = {}
    
    for column in columns_to_analyze:
        if df_subset[column].dtype not in ['int64', 'float64']:
            continue
            
        subsequence = df_subset[column]
        col_violations = 0
        
        if direction == 'increasing':
            for i in range(1, len(subsequence)):
                decrease = subsequence.iloc[i-1] - subsequence.iloc[i]
                if decrease > tolerance:
                    col_violations += 1
        elif direction == 'decreasing':
            for i in range(1, len(subsequence)):
                increase = subsequence.iloc[i] - subsequence.iloc[i-1]
                if increase > tolerance:
                    col_violations += 1
        
        violations[column] = col_violations
    
    return violations

def analyze_monotonic_patterns_all_cols(df, columns_to_analyze=None, tolerance=0.05):
    """
    Analyze monotonic patterns across ALL columns simultaneously.
    Only classifies as monotonic if ALL columns consistently go in the same direction.
    
    Args:
        df: pandas DataFrame
        columns_to_analyze: List of column names to analyze (default: first 5 columns)
        tolerance: Maximum allowed counter-movement (default: 0.05)
    
    Returns:
        Dictionary with analysis results
    """
    if columns_to_analyze is None:
        columns_to_analyze = df.columns[:5]
    
    print(f"Analyzing monotonic patterns across ALL columns: {list(columns_to_analyze)}")
    print(f"Tolerance: {tolerance}")
    print("="*70)
    
    # Find monotonic intervals across all columns
    intervals = find_monotonic_intervals_all_cols(df, tolerance, columns_to_analyze)
    
    # Merge adjacent intervals of the same type
    merged_intervals = merge_adjacent_intervals(intervals)
    
    # Separate by type
    increasing_intervals = [i for i in merged_intervals if i['type'] == 'increasing']
    decreasing_intervals = [i for i in merged_intervals if i['type'] == 'decreasing']
    
    # Store results
    results = {
        'raw_intervals': intervals,
        'merged_intervals': merged_intervals,
        'total_intervals': len(merged_intervals),
        'increasing_intervals': increasing_intervals,
        'decreasing_intervals': decreasing_intervals,
        'columns_analyzed': columns_to_analyze
    }
    
    # Print summary
    print(f"Total merged intervals: {len(merged_intervals)}")
    print(f"Increasing intervals (all columns): {len(increasing_intervals)}")
    print(f"Decreasing intervals (all columns): {len(decreasing_intervals)}")
    
    # Print detailed information about merged intervals
    print(f"\nMerged Intervals (tolerance={tolerance}):")
    for i, interval in enumerate(merged_intervals):
        # Calculate violations for this interval
        df_subset = df.iloc[interval['start']:interval['end']+1]
        violations = count_tolerance_violations_all_cols(df_subset, interval['type'], tolerance, columns_to_analyze)
        total_violations = sum(violations.values())
        
        print(f"\n  {i+1}. {interval['type'].upper()} interval:")
        print(f"     Indices: {interval['start']}-{interval['end']}")
        print(f"     Length: {interval['length']}")
        print(f"     Total violations: {total_violations}")
        print(f"     Changes by column:")
        for col in columns_to_analyze:
            if col in interval['changes']:
                print(f"       {col}: {interval['changes'][col]:.6f} (violations: {violations.get(col, 0)})")
        print(f"     Total change: {interval['total_change']:.6f}")
    
    return results

# Read the CSV file
df = pd.read_csv('data.csv')

print("Original data shape:", df.shape)
print("\nFirst few rows of original data:")
print(df.head())

# Analyze monotonic patterns across all columns with tolerance of 0.05
results = analyze_monotonic_patterns_all_cols(df, df.columns[:5], tolerance=0.05)

# Create visualizations
def plot_monotonic_intervals_all_cols(df, columns_to_analyze, intervals, max_points=1000):
    """
    Plot all analyzed columns with monotonic intervals highlighted.
    """
    # Sample data if too large for plotting
    if len(df) > max_points:
        step = len(df) // max_points
        plot_df = df.iloc[::step].copy()
        plot_df.reset_index(drop=True, inplace=True)
        # Adjust intervals for sampled data
        adjusted_intervals = []
        for interval in intervals:
            adj_start = interval['start'] // step
            adj_end = min(interval['end'] // step, len(plot_df) - 1)
            if adj_start < adj_end:
                adjusted_intervals.append({
                    **interval,
                    'start': adj_start,
                    'end': adj_end
                })
        intervals = adjusted_intervals
    else:
        plot_df = df.copy()
    
    # Create subplots for each column
    fig, axes = plt.subplots(len(columns_to_analyze), 1, figsize=(15, 4 * len(columns_to_analyze)))
    if len(columns_to_analyze) == 1:
        axes = [axes]
    
    fig.suptitle('Monotonic Intervals Across All Columns (Synchronized)', fontsize=16)
    
    colors = {'increasing': 'green', 'decreasing': 'red'}
    
    for idx, column in enumerate(columns_to_analyze):
        if column in plot_df.columns:
            axes[idx].plot(plot_df.index, plot_df[column], 'b-', alpha=0.7, linewidth=1)
            
            # Color intervals
            for interval in intervals:
                start_idx = interval['start']
                end_idx = min(interval['end'], len(plot_df) - 1)
                if start_idx < end_idx:
                    axes[idx].axvspan(start_idx, end_idx, 
                                    color=colors[interval['type']], alpha=0.3)
            
            axes[idx].set_title(f'{column}')
            axes[idx].set_xlabel('Data Point Index')
            axes[idx].set_ylabel('Value')
            axes[idx].grid(True, alpha=0.3)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', alpha=0.3, label='Increasing (All Columns)'),
        Patch(facecolor='red', alpha=0.3, label='Decreasing (All Columns)')
    ]
    axes[0].legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.show()

# Plot monotonic intervals for all columns
plot_monotonic_intervals_all_cols(df, df.columns[:5], results['merged_intervals'])

# Summary statistics
print("\n" + "="*70)
print("SUMMARY STATISTICS - ALL COLUMNS SYNCHRONIZED")
print("="*70)

merged_intervals = results['merged_intervals']
increasing_intervals = results['increasing_intervals']
decreasing_intervals = results['decreasing_intervals']

print(f"\nColumns analyzed: {results['columns_analyzed']}")
print(f"Total synchronized monotonic intervals: {len(merged_intervals)}")
print(f"Synchronized increasing intervals: {len(increasing_intervals)}")
print(f"Synchronized decreasing intervals: {len(decreasing_intervals)}")

if increasing_intervals:
    avg_inc_length = np.mean([i['length'] for i in increasing_intervals])
    max_inc_length = max([i['length'] for i in increasing_intervals])
    total_inc_change = sum([i['total_change'] for i in increasing_intervals])
    print(f"\nIncreasing intervals statistics:")
    print(f"  Average length: {avg_inc_length:.1f}")
    print(f"  Maximum length: {max_inc_length}")
    print(f"  Total change (all columns): {total_inc_change:.6f}")

if decreasing_intervals:
    avg_dec_length = np.mean([i['length'] for i in decreasing_intervals])
    max_dec_length = max([i['length'] for i in decreasing_intervals])
    total_dec_change = sum([i['total_change'] for i in decreasing_intervals])
    print(f"\nDecreasing intervals statistics:")
    print(f"  Average length: {avg_dec_length:.1f}")
    print(f"  Maximum length: {max_dec_length}")
    print(f"  Total change (all columns): {total_dec_change:.6f}")

# Save results to CSV
print("\n" + "="*70)
print("SAVING RESULTS")
print("="*70)

# Create a summary dataframe
summary_data = []
for i, interval in enumerate(results['merged_intervals']):
    # Base row data
    row_data = {
        'interval_id': i + 1,
        'type': interval['type'],
        'start_index': interval['start'],
        'end_index': interval['end'],
        'length': interval['length'],
        'total_change': interval['total_change']
    }
    
    # Add individual column data
    for col in results['columns_analyzed']:
        if col in interval['start_values']:
            row_data[f'{col}_start'] = interval['start_values'][col]
            row_data[f'{col}_end'] = interval['end_values'][col]
            row_data[f'{col}_change'] = interval['changes'][col]
    
    summary_data.append(row_data)

summary_df = pd.DataFrame(summary_data)
summary_df.to_csv('monotonic_intervals_all_columns_summary.csv', index=False)
print("Synchronized monotonic intervals summary saved to 'monotonic_intervals_all_columns_summary.csv'")

print("\nAnalysis complete!")
print(f"Found {len(results['merged_intervals'])} intervals where ALL {len(results['columns_analyzed'])} columns move together monotonically.")
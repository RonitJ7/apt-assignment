import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_line_smoothness(data):
    """Calculate smoothness of a line graph"""
    # Method 1: Standard deviation of first differences (lower = smoother)
    first_diff = np.diff(data)
    smoothness_std = np.std(first_diff)
    
    # Method 2: Mean absolute deviation of first differences
    smoothness_mad = np.mean(np.abs(first_diff - np.mean(first_diff)))
    
    # Method 3: Total variation (sum of absolute differences)
    total_variation = np.sum(np.abs(first_diff))
    
    # Method 4: Smoothness score (0-1, higher = smoother)
    # Based on normalized inverse of variance of differences
    if len(first_diff) > 0:
        variance_diff = np.var(first_diff)
        smoothness_score = 1 / (1 + variance_diff)
    else:
        smoothness_score = 1.0
    
    return {
        'std_of_differences': smoothness_std,
        'mean_abs_deviation': smoothness_mad,
        'total_variation': total_variation,
        'smoothness_score': smoothness_score
    }

def plot_all_variables(df):
    """Plot all variables as line graphs against time (index)"""
    # Get all numeric columns
    numeric_cols = ['deltaX', 'gamma', 'omega', 'flux', 'pulse', 'neutronCount']
    
    # Create time axis (using index as time)
    time_axis = df.index
    
    # Create subplots
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Line Graphs of All Variables vs Time', fontsize=16, fontweight='bold')
    
    # Flatten axes for easier iteration
    axes = axes.flatten()
    
    # Plot each variable
    for i, col in enumerate(numeric_cols):
        if col in df.columns:
            axes[i].plot(time_axis, df[col], linewidth=0.8, alpha=0.8)
            axes[i].set_title(f'{col} vs Time')
            axes[i].set_xlabel('Time (Index)')
            axes[i].set_ylabel(col)
            axes[i].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Also create a combined plot
    plt.figure(figsize=(15, 8))
    
    # Plot all variables except neutronCount (different scale)
    for col in ['deltaX', 'gamma', 'omega', 'flux', 'pulse']:
        if col in df.columns:
            plt.plot(time_axis, df[col], label=col, linewidth=0.8, alpha=0.8)
    
    plt.title('All Variables vs Time (Combined)', fontsize=14, fontweight='bold')
    plt.xlabel('Time (Index)')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
    
    # Separate plot for neutronCount due to different scale
    plt.figure(figsize=(15, 6))
    plt.plot(time_axis, df['neutronCount'], color='red', linewidth=0.8)
    plt.title('Neutron Count vs Time', fontsize=14, fontweight='bold')
    plt.xlabel('Time (Index)')
    plt.ylabel('Neutron Count')
    plt.grid(True, alpha=0.3)
    plt.show()

def analyze_line_smoothness(df):
    """Analyze smoothness of all line graphs"""
    print("\n" + "="*60)
    print("LINE GRAPH SMOOTHNESS ANALYSIS")
    print("="*60)
    
    variables = ['deltaX', 'gamma', 'omega', 'flux', 'pulse', 'neutronCount']
    results = []
    
    for var in variables:
        if var in df.columns:
            smoothness = calculate_line_smoothness(df[var].values)
            results.append({
                'Variable': var,
                'Std of Differences': smoothness['std_of_differences'],
                'Mean Abs Deviation': smoothness['mean_abs_deviation'],
                'Total Variation': smoothness['total_variation'],
                'Smoothness Score': smoothness['smoothness_score']
            })
    
    # Create results dataframe
    results_df = pd.DataFrame(results)
    
    # Display results
    print("\nSmootness Metrics for Each Line Graph:")
    print("-" * 80)
    
    for _, row in results_df.iterrows():
        print(f"\n{row['Variable'].upper()}:")
        print(f"  Standard Deviation of Differences: {row['Std of Differences']:.6f}")
        print(f"  Mean Absolute Deviation: {row['Mean Abs Deviation']:.6f}")
        print(f"  Total Variation: {row['Total Variation']:.2f}")
        print(f"  Smoothness Score (0-1): {row['Smoothness Score']:.6f}")
    
    # Ranking by smoothness score
    print("\n" + "="*60)
    print("SMOOTHNESS RANKING (Most to Least Smooth Lines):")
    print("="*60)
    
    ranking = results_df.sort_values('Smoothness Score', ascending=False)
    for i, (_, row) in enumerate(ranking.iterrows(), 1):
        print(f"{i}. {row['Variable']}: {row['Smoothness Score']:.6f}")
    
    # Create bar chart of smoothness scores
    plt.figure(figsize=(12, 6))
    bars = plt.bar(results_df['Variable'], results_df['Smoothness Score'], 
                   color=plt.cm.viridis(np.linspace(0, 1, len(results_df))))
    
    plt.title('Line Graph Smoothness Comparison', fontsize=14, fontweight='bold')
    plt.xlabel('Variables')
    plt.ylabel('Smoothness Score (Higher = Smoother)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, score in zip(bars, results_df['Smoothness Score']):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{score:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.show()
    
    return results_df

def main():
    """Main function"""
    # Load data
    print("Loading data from 'data.csv'...")
    try:
        df = pd.read_csv('data.csv')
        # Clean column names
        df.columns = df.columns.str.strip()
        print(f"Data loaded successfully! Shape: {df.shape}")
    except FileNotFoundError:
        print("Error: 'data.csv' file not found!")
        return
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    # Plot all variables as line graphs
    plot_all_variables(df)
    
    # Analyze smoothness of each line
    results_df = analyze_line_smoothness(df)
    
    print("\n" + "="*60)
    print("INTERPRETATION:")
    print("="*60)
    print("• Smoothness Score: 0-1 scale, higher = smoother line")
    print("• Standard Deviation of Differences: Lower = smoother transitions")
    print("• Mean Absolute Deviation: Lower = more consistent changes")
    print("• Total Variation: Lower = less overall fluctuation")
    print("\nA smooth line has:")
    print("- High smoothness score (close to 1)")
    print("- Low standard deviation of differences")
    print("- Low total variation")

if __name__ == "__main__":
    main()
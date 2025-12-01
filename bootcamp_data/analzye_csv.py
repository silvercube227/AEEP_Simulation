import pandas as pd
import numpy as np

# === Step 1: Load the CSV ===
file_path = '/Users/gracenoh/Downloads/force_log (3).csv'

# Define column names (1 timestamp + 14 sensors)
cols = ['timestamp'] + [f'force_{i+1}' for i in range(14)]
df = pd.read_csv(file_path, names=cols, skiprows=1)

# === Step 2: Remove timestamp and first 4 sensors ===
df = df.drop(columns=['timestamp'] + [f'force_{i+1}' for i in range(4)])

# === Step 3: Rename remaining 10 sensors ===
sensor_names = [f'sensor A{i}' for i in range(4, 14)]  # A4 → A13
df.columns = sensor_names

# === Step 4: Dynamically input the range of interest ===
# Lines are 1-indexed in your description, so convert to zero-based indexing
start_line = int(input("Enter the starting line number (e.g., 488): "))
end_line = int(input("Enter the ending line number (e.g., 514): "))

subset = df.iloc[start_line - 1:end_line]  # inclusive range

# === Step 5: Save the raw sensor values ===
raw_output_path = f'/Users/gracenoh/Downloads/raw_sensor_values_{start_line}_{end_line}.csv'
subset.to_csv(raw_output_path, index=False)
print(f"✅ Raw sensor values saved to: {raw_output_path}")

# === Step 6: Compute statistics for each sensor ===
stats = {}
for col in subset.columns:
    values = subset[col]
    stats[col] = {
        'min': values.min(),
        'max': values.max(),
        'mean': values.mean(),
        'median': values.median(),
        'max-min magnitude': abs(values.max() - values.min()),
        'std_dev': values.std(),
        'variance': values.var()
    }

stats_df = pd.DataFrame(stats).T

# === Step 7: Save statistics ===
stats_output_path = f'/Users/gracenoh/Downloads/sensor_stats_{start_line}_{end_line}.csv'
stats_df.to_csv(stats_output_path)
print(f"✅ Statistics saved to: {stats_output_path}")

# === Step 8: Optional — print summary ===
print("\nRaw sensor values (first few rows):")
print(subset.head())

print("\nStatistics summary:")
print(stats_df)
print(f"\nNumber of sensors analyzed: {len(stats_df)}")

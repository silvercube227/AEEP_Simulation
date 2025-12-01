import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV file
df = pd.read_csv('master/force_sensing/EA6/quadrant_log.csv')

# Convert timestamp to float and create delta_t
df['timestamp'] = df['timestamp'].astype(float)

# Detect calibration end by finding first significant change
df['total_directional'] = df['N'] + df['S'] + df['E'] + df['W']
calibration_threshold = 1.0
calibration_end_idx = df[df['total_directional'] > calibration_threshold].index
if len(calibration_end_idx) > 0:
    start_idx = calibration_end_idx[0]
else:
    start_idx = 0

# Filter data to only include post-calibration
df = df.iloc[start_idx:].copy()
df['delta_t'] = df['timestamp'] - df['timestamp'].iloc[0]

# Create subplots
fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(16, 12))
axs = axs.flatten()

# Plots 1-4: Directional forces (N, S, E, W)
directions = ['N', 'S', 'E', 'W']
for i, direction in enumerate(directions):
    axs[i].plot(df['delta_t'], df[direction])
    axs[i].set_title(f'{direction} Direction Force')
    axs[i].set_ylabel('Force Reading')
    
    nonzero_values = df[direction][df[direction] != 0]
    if len(nonzero_values) > 0:
        min_val = nonzero_values.min()
        max_val = nonzero_values.max()
        avg_val = nonzero_values.mean()
    else:
        min_val = 0
        max_val = df[direction].max()
        avg_val = df[direction].mean()
    
    stats_text = f'Min: {min_val:.2f}\nMax: {max_val:.2f}\nAvg: {avg_val:.2f}'
    axs[i].text(0.02, 0.98, stats_text, transform=axs[i].transAxes, fontsize=9,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Plot 5: Quadrant distribution (bar chart)
quadrant_counts = df['quadrant'].value_counts()
axs[4].bar(range(len(quadrant_counts)), quadrant_counts.values)
axs[4].set_xticks(range(len(quadrant_counts)))
axs[4].set_xticklabels(quadrant_counts.index, rotation=45)
axs[4].set_title('Quadrant Distribution')
axs[4].set_ylabel('Count')

# Remove extra subplot
fig.delaxes(axs[5])

# Set x-axis ticks for time-series plots
tick_increment = 30
max_time = df['delta_t'].max()
x_ticks = np.arange(0, max_time + tick_increment, tick_increment)
for ax in axs[:4]:  # First 4 plots are time-series
    ax.set_xticks(x_ticks)
    ax.tick_params(axis='x', rotation=0, labelsize=8)
    # Set y-axis ticks
    y_max = ax.get_ylim()[1]
    y_tick_increment = 10
    y_ticks = np.arange(0, y_max + y_tick_increment, y_tick_increment)
    ax.set_yticks(y_ticks)
    ax.tick_params(axis='y', labelsize=8)

# Add x-axis label
fig.text(0.5, 0.02, 'Time (s)', ha='center', fontsize=12)

plt.tight_layout()
plt.subplots_adjust(bottom=0.05)
plt.show()
#plots force over time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

cols = ['timestamp'] + [f'force_{i+1}' for i in range(14)]
df = pd.read_csv('master/force_sensing/EA6/force_log.csv', names=cols, skiprows=1)

df['timestamp'] = df['timestamp'].astype(float)

# Detect calibration end by finding the first significant jump in data
# Calculate the sum of all force readings per row
df['total_force'] = df[[f'force_{i+1}' for i in range(14)]].sum(axis=1)

# Find where calibration ends (first significant increase)
# Look for first row where total force exceeds a threshold (e.g., 1.0)
calibration_threshold = 1.0
calibration_end_idx = df[df['total_force'] > calibration_threshold].index
if len(calibration_end_idx) > 0:
    start_idx = calibration_end_idx[0]
else:
    start_idx = 0  # If no jump detected, use all data

# Filter data to only include post-calibration
df = df.iloc[start_idx:].copy()

# Convert timestamp to delta t (time elapsed from calibration end in seconds)
df['delta_t'] = df['timestamp'] - df['timestamp'].iloc[0]

# Prepare subplots (grid with 3 columns)
num_sensors = 14
fig, axs = plt.subplots(nrows=5, ncols=3, figsize=(18, 12), sharex=True)
axs = axs.flatten()  # To simplify iteration

for i in range(num_sensors):
    sensor_col = f'force_{i+1}'
    
    # Calculate statistics (only for non-zero values)
    nonzero_values = df[sensor_col][df[sensor_col] != 0]
    if len(nonzero_values) > 0:
        min_val = nonzero_values.min()
        max_val = nonzero_values.max()
        avg_val = nonzero_values.mean()
    else:
        min_val = 0
        max_val = df[sensor_col].max()
        avg_val = df[sensor_col].mean()
    
    # Plot the data
    axs[i].plot(df['delta_t'], df[sensor_col])
    axs[i].set_title(f'{sensor_col}')
    axs[i].set_ylabel('Force Reading')
    
    # Set y-axis tick increments
    y_tick_increment = 5  # Change this value to adjust y-axis spacing (e.g., 5, 10, 20, etc.)
    y_max = df[sensor_col].max()
    y_ticks = np.arange(40, y_max + y_tick_increment, y_tick_increment)
    axs[i].set_yticks(y_ticks)
    axs[i].tick_params(axis='y', labelsize=8)
    
    # Add statistics as text on the plot
    stats_text = f'Min: {min_val:.2f}\nMax: {max_val:.2f}\nAvg: {avg_val:.2f}'
    axs[i].text(0.02, 0.98, stats_text, 
                transform=axs[i].transAxes, 
                fontsize=9, 
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Remove extra subplots
for j in range(num_sensors, len(axs)):
    fig.delaxes(axs[j])

# Set x-axis tick increments (change the number to your desired increment in seconds)
tick_increment = 10  # Increased spacing to reduce overlap
max_time = df['delta_t'].max()
import numpy as np
x_ticks = np.arange(0, max_time + tick_increment, tick_increment)
for ax in axs[:num_sensors]:
    ax.set_xticks(x_ticks)
    ax.tick_params(axis='x', rotation=0, labelsize=8)  # Horizontal labels with smaller font

# Add x-axis label to all bottom row subplots
fig.text(0.5, 0.02, 'Time (s)', ha='center', fontsize=12)

plt.tight_layout()
plt.subplots_adjust(bottom=0.05)  
plt.show()
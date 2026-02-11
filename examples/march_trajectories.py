import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Load the data
df = pd.read_csv('/sessions/eager-elegant-bardeen/auckland-pedestrian/src/auckland_pedestrian/data/hourly_counts.csv')
df['date'] = pd.to_datetime(df['date'])

# Extract month from date
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day

# Filter to March only
march_df = df[df['month'] == 3].copy()

# Get sensor columns (all columns except date, hour, year, month, day)
sensor_cols = [col for col in march_df.columns if col not in ['date', 'hour', 'year', 'month', 'day']]

# Select 9 key sensors
sensors_to_plot = [
    "45 Queen Street",
    "210 Queen Street",
    "297 Queen Street",
    "107 Quay Street",
    "2 High Street",
    "150 K Road",
    "183 K Road",
    "Commerce Street West",
    "19 Shortland Street"
]

# Verify sensors exist
available_sensors = [s for s in sensors_to_plot if s in sensor_cols]
print(f"Found {len(available_sensors)} out of {len(sensors_to_plot)} sensors")
print(f"Available sensors: {available_sensors}")

# Group by year and day, sum across all hours to get daily totals
daily_march = march_df.groupby(['year', 'day'])[available_sensors].sum().reset_index()

# Create color palette for years (2019-2025)
years = sorted(daily_march['year'].unique())
palette = sns.color_palette("viridis", len(years))
year_colors = {year: palette[i] for i, year in enumerate(years)}

# Create 3x3 subplot grid
fig, axes = plt.subplots(3, 3, figsize=(14, 10))
axes = axes.flatten()

# Set style
sns.set_style("whitegrid")

# Plot each sensor
for idx, sensor in enumerate(available_sensors):
    ax = axes[idx]
    
    # Plot line for each year
    for year in years:
        year_data = daily_march[daily_march['year'] == year]
        ax.plot(year_data['day'], year_data[sensor], 
                marker='o', markersize=4, linewidth=1.5,
                label=str(year), color=year_colors[year], alpha=0.8)
    
    # Format subplot
    ax.set_xlabel('Day of March', fontsize=9)
    ax.set_ylabel('Daily Footfall', fontsize=9)
    
    # Shorten sensor name if too long
    short_name = sensor if len(sensor) <= 20 else sensor[:17] + '...'
    ax.set_title(short_name, fontsize=10, fontweight='bold')
    
    ax.set_xlim(1, 31)
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=8)

# Remove extra subplots
for idx in range(len(available_sensors), 9):
    fig.delaxes(axes[idx])

# Create shared legend
handles = [plt.Line2D([0], [0], color=year_colors[year], linewidth=2, marker='o', markersize=5, label=str(year)) 
           for year in years]
fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, 0.98), 
           ncol=len(years), frameon=True, fontsize=10, title='Year')

# Adjust layout
plt.tight_layout(rect=[0, 0, 1, 0.96])

# Create output directory if needed
import os
output_dir = '/sessions/eager-elegant-bardeen/auckland-pedestrian/examples'
os.makedirs(output_dir, exist_ok=True)

# Save figure
output_path = os.path.join(output_dir, 'march_trajectories.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\nPlot saved to {output_path}")

plt.close()

# Print summary stats
print("\nSummary Statistics:")
print(f"Years covered: {years}")
print(f"Sensors plotted: {len(available_sensors)}")
print(f"March data range: {march_df['date'].min()} to {march_df['date'].max()}")

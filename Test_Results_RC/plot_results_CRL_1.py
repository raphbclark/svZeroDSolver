import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

# 1. Load the CSV 
df = pd.read_csv('Test_Results_RC/adapted_sim_1.csv', sep=r'[,\s]+', engine='python')
df.columns = df.columns.str.strip()

# 2. Pivot the data from "long" to "wide" format
df_wide = df.pivot(index='time', columns='name', values='y').reset_index()

# 3. Create a layout with 3 plots
fig = plt.figure(figsize=(14, 7))
ax1 = plt.subplot(2, 2, 1) # Top-left
ax2 = plt.subplot(2, 2, 3, sharex=ax1) # Bottom-left
ax3 = plt.subplot(1, 2, 2) # Right-half

# --- Plot 1: Pressures ---
# Looking for any column containing 'pressure:'
pressure_cols = [col for col in df_wide.columns if 'pressure:' in col]
for col in pressure_cols:
    ax1.plot(df_wide['time'], df_wide[col], label=col)
ax1.set_title('Pressures over Time')
ax1.set_ylabel('Pressure (dynes/cm²)')
ax1.grid(True)
if pressure_cols:
    # Fontsize reduced slightly to fit the longer colon-separated names
    ax1.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fontsize='x-small')

# --- Plot 2: Flows and Volumes ---
# Looking for any column containing 'flow:' or 'volume:'
flow_cols = [col for col in df_wide.columns if 'flow:' in col or 'volume:' in col]
for col in flow_cols:
    ax2.plot(df_wide['time'], df_wide[col], label=col)
ax2.set_title('Flows and Volumes over Time')
ax2.set_ylabel('Flow (cm³/s) / Volume (cm³)')
ax2.set_xlabel('Time (s)')
ax2.grid(True)
if flow_cols:
    ax2.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fontsize='x-small')

# --- Plot 3: P-V Loop (Colored by Time) ---
# Using the EXACT variable names from your solver output
vol_col = 'volume:ventricle'
pres_col = 'pressure:ventricle:outlet_valve' 

if vol_col in df_wide.columns and pres_col in df_wide.columns:
    # Drop any blank rows to ensure a continuous line
    loop_data = df_wide[['time', vol_col, pres_col]].dropna()
    
    x = loop_data[vol_col].values
    y = loop_data[pres_col].values
    t = loop_data['time'].values

    # Break the line into tiny segments to apply the color gradient
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Create a gradient using the 'plasma' colormap
    norm = plt.Normalize(t.min(), t.max())
    lc = LineCollection(segments, cmap='plasma', norm=norm)
    lc.set_array(t)
    lc.set_linewidth(1.5)
    
    line = ax3.add_collection(lc)
    ax3.autoscale()
    
    cbar = fig.colorbar(line, ax=ax3)
    cbar.set_label('Time (seconds)')
    
    # Calculate Cardiac Metrics from the final stabilized cycle (last 1.0 second)
    max_time = t.max()
    last_cycle = loop_data[loop_data['time'] >= (max_time - 1.0)]
    if not last_cycle.empty:
        edv = last_cycle[vol_col].max()
        esv = last_cycle[vol_col].min()
        sv = edv - esv
        ef = (sv / edv) * 100
        
        # Display the metrics in a text box on the plot
        stats_text = f"Final Cycle Metrics:\nEDV: {edv:.1f} cm³\nESV: {esv:.1f} cm³\nSV: {sv:.1f} cm³\nEF: {ef:.1f}%"
        ax3.text(0.95, 0.05, stats_text, transform=ax3.transAxes, 
                 fontsize=10, verticalalignment='bottom', horizontalalignment='right',
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    ax3.set_title('Ventricular P-V Loop (Progression)')
    ax3.set_xlabel('Volume (cm³)')
    ax3.set_ylabel('Pressure (dynes/cm²)')
    ax3.grid(True)
else:
    ax3.text(0.5, 0.5, 'Exact Ventricle Volume/Pressure strings not found', ha='center', va='center')

plt.tight_layout()
plt.show()
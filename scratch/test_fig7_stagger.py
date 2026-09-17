import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

df = pd.read_csv('data/raw/air_quality/epd_air_quality_2019_2021_hourly.csv')
CRITERIA = ['pm25', 'pm10', 'no2', 'so2', 'o3']
df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
df['missing'] = df[CRITERIA].isna().sum(axis=1)
total_missing = df['missing'].sum()

h_df = df.groupby('hour')['missing'].sum().reset_index()
h_df['pct'] = h_df['missing'] / total_missing * 100

sns.set_theme(style="white")
fig, ax = plt.subplots(figsize=(11, 9))

# Seaborn color palette
palette = sns.color_palette("tab20", 20) + sns.color_palette("tab20b", 4)

wedges, texts = ax.pie(
    h_df['pct'],
    colors=palette,
    startangle=90,
    counterclock=False,
    wedgeprops=dict(edgecolor="white", linewidth=1.0)
)

# Manage text and values placement so each is placed to its corresponding wedge
for i, p in enumerate(wedges):
    ang = (p.theta2 - p.theta1) / 2.0 + p.theta1
    rad = np.deg2rad(ang)
    row = h_df.iloc[i]
    h = int(row['hour'])
    pct = row['pct']
    cnt = int(row['missing'])
    
    # Base direction
    x = np.cos(rad)
    y = np.sin(rad)
    
    # If slice is small (e.g. pct < 3.5%), stagger radial distance
    # to completely eliminate overlap in crowded regions (hours 5-8, 15-22)
    if pct < 3.0:
        dist = 1.28 if (h % 2 == 1) else 1.10
        # Draw a small subtle connecting line if dist > 1.12
        if dist > 1.15:
            ax.plot([x * 1.01, x * (dist - 0.05)], [y * 1.01, y * (dist - 0.05)], color="#888", lw=0.6)
    else:
        dist = 1.12
        
    ha = "left" if x >= 0 else "right"
    va = "center"
    
    label = f"{h:02d}:00\n{pct:.1f}% ({cnt:,})" if pct >= 5.0 else f"{h:02d}:00 ({pct:.1f}%)"
    
    ax.text(
        x * dist, y * dist,
        label,
        ha=ha, va=va,
        fontsize=8,
        color="#222"
    )

ax.set_title("Proportion of Hourly Missing Data in Total Missing Data (CTDI Fig. 7)\n(Default Style of Seaborn / Matplotlib with Managed Placement)", fontsize=13, fontweight="bold", pad=20)
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
plt.savefig("scratch/test_fig7_stagger.png", dpi=200)
plt.close()
print("Staggered Fig 7 saved.")

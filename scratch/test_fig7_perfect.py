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

sns.set_theme(style="white", font="sans-serif")
fig, ax = plt.subplots(figsize=(13, 11))
palette7 = sns.color_palette("tab20", 20) + sns.color_palette("tab20b", 4)

wedges7, _ = ax.pie(
    h_df['pct'],
    colors=palette7,
    startangle=90,
    counterclock=False,
    wedgeprops=dict(edgecolor="white", linewidth=1.2)
)

for i, p in enumerate(wedges7):
    ang = (p.theta2 - p.theta1) / 2.0 + p.theta1
    rad = np.deg2rad(ang)
    x = np.cos(rad)
    y = np.sin(rad)
    row = h_df.iloc[i]
    h = int(row['hour'])
    pct = row['pct']
    cnt = int(row['missing'])
    
    # 3-tier radial stagger for small crowded slices (pct < 3.2%)
    if pct < 3.2:
        tier = h % 3
        dist = 1.10 if tier == 0 else (1.24 if tier == 1 else 1.38)
        if dist > 1.12:
            ax.plot([x * 1.01, x * (dist - 0.03)], [y * 1.01, y * (dist - 0.03)], color="#888", lw=0.6)
    elif pct < 5.0:
        dist = 1.12
    else:
        dist = 1.14
        
    # Smart alignment based on position around circle
    if abs(x) < 0.25:
        ha = "center"
        va = "bottom" if y > 0 else "top"
    else:
        ha = "left" if x > 0 else "right"
        va = "center"
    
    if pct >= 5.0:
        label = f"{h:02d}:00\n{pct:.2f}%\n({cnt:,})"
    else:
        label = f"{h:02d}:00\n{pct:.2f}% ({cnt:,})"
    
    ax.text(
        x * dist, y * dist,
        label,
        ha=ha, va=va,
        fontsize=8.5,
        color="#1a202c"
    )

ax.set_xlim(-1.6, 1.6)
ax.set_ylim(-1.6, 1.6)
ax.set_title("Proportion of Hourly Missing Data in Total Missing Data (CTDI Fig. 7)\n(Seaborn / Matplotlib Style)", fontsize=13, fontweight="bold", pad=20)
plt.subplots_adjust(left=0.08, right=0.92, top=0.92, bottom=0.08)
plt.savefig("scratch/fig7_perfect.png", dpi=200)
plt.close()
print("Fig 7 perfect saved.")

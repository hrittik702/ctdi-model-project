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
fig, ax = plt.subplots(figsize=(13, 9))
palette = sns.color_palette("tab20", 24)

wedges, _ = ax.pie(
    h_df['pct'],
    colors=palette,
    startangle=90,
    counterclock=False,
    wedgeprops=dict(edgecolor="white", linewidth=1.0)
)

left_items = []
right_items = []

for i, p in enumerate(wedges):
    # Midpoint of wedge angle
    ang = (p.theta2 - p.theta1) / 2.0 + p.theta1
    rad = np.deg2rad(ang)
    x = np.cos(rad)
    y = np.sin(rad)
    row = h_df.iloc[i]
    label = f"{int(row['hour']):02d}:00 — {row['pct']:.2f}% ({int(row['missing']):,})"
    item = {"index": i, "x": x, "y": y, "ang": ang, "label": label, "wedge": p}
    if x >= 0:
        right_items.append(item)
    else:
        left_items.append(item)

# Sort by y descending
right_items.sort(key=lambda item: item['y'], reverse=True)
left_items.sort(key=lambda item: item['y'], reverse=True)

if right_items:
    y_right = np.linspace(1.25, -1.25, len(right_items))
    for item, y_t in zip(right_items, y_right):
        ax.annotate(
            item['label'],
            xy=(item['x'], item['y']),
            xytext=(1.45, y_t),
            arrowprops=dict(arrowstyle="-", color="#777", lw=0.75, connectionstyle="angle,angleA=0,angleB=90,rad=0"),
            fontsize=8,
            va="center",
            ha="left"
        )

if left_items:
    y_left = np.linspace(1.25, -1.25, len(left_items))
    for item, y_t in zip(left_items, y_left):
        ax.annotate(
            item['label'],
            xy=(item['x'], item['y']),
            xytext=(-1.45, y_t),
            arrowprops=dict(arrowstyle="-", color="#777", lw=0.75, connectionstyle="angle,angleA=0,angleB=90,rad=0"),
            fontsize=8,
            va="center",
            ha="right"
        )

ax.set_xlim(-2.4, 2.4)
ax.set_ylim(-1.4, 1.4)
ax.set_title("Proportion of Hourly Missing Data in Total Missing Data (CTDI Fig. 7)\n(Seaborn / Matplotlib Style with Managed Text Placement)", fontsize=13, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig("scratch/test_fig7_aligned.png", dpi=200)
plt.close()
print("Fig 7 aligned callouts generated.")

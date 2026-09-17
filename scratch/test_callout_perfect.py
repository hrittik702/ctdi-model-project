import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

df = pd.read_csv('data/raw/air_quality/epd_air_quality_2019_2021_hourly.csv')
CRITERIA = ['pm25', 'pm10', 'no2', 'so2', 'o3']
df['missing'] = df[CRITERIA].isna().sum(axis=1)
total_missing = df['missing'].sum()

st = df.groupby('station_name')['missing'].sum().reset_index()
st['pct'] = st['missing'] / total_missing * 100
st = st.sort_values('pct', ascending=False).reset_index(drop=True)

sns.set_theme(style="white")
fig, ax = plt.subplots(figsize=(12, 8))
palette = sns.color_palette("tab20", 16)

# Standard pie chart
wedges, _ = ax.pie(
    st['pct'],
    colors=palette,
    startangle=90,
    wedgeprops=dict(edgecolor="white", linewidth=1.2)
)

# Callout lines with aligned text on left and right
# Extract angles and split into left and right
left_items = []
right_items = []

for i, p in enumerate(wedges):
    ang = (p.theta2 - p.theta1) / 2.0 + p.theta1
    rad = np.deg2rad(ang)
    x = np.cos(rad)
    y = np.sin(rad)
    row = st.iloc[i]
    label = f"{row['station_name']}: {row['pct']:.2f}% ({row['missing']:,})"
    item = {"index": i, "x": x, "y": y, "ang": ang, "label": label, "wedge": p}
    if x >= 0:
        right_items.append(item)
    else:
        left_items.append(item)

# Sort right items by y descending
right_items.sort(key=lambda item: item['y'], reverse=True)
# Sort left items by y descending
left_items.sort(key=lambda item: item['y'], reverse=True)

# Assign evenly spaced y_text to prevent any overlap
if right_items:
    y_right = np.linspace(1.15, -1.15, len(right_items))
    for item, y_t in zip(right_items, y_right):
        ax.annotate(
            item['label'],
            xy=(item['x'], item['y']),
            xytext=(1.4, y_t),
            arrowprops=dict(arrowstyle="-", color="#666", lw=0.8, connectionstyle="angle,angleA=0,angleB=90,rad=0"),
            fontsize=8.5,
            fontweight="medium",
            va="center",
            ha="left"
        )

if left_items:
    y_left = np.linspace(1.15, -1.15, len(left_items))
    for item, y_t in zip(left_items, y_left):
        ax.annotate(
            item['label'],
            xy=(item['x'], item['y']),
            xytext=(-1.4, y_t),
            arrowprops=dict(arrowstyle="-", color="#666", lw=0.8, connectionstyle="angle,angleA=0,angleB=90,rad=0"),
            fontsize=8.5,
            fontweight="medium",
            va="center",
            ha="right"
        )

ax.set_xlim(-2.2, 2.2)
ax.set_ylim(-1.3, 1.3)
ax.set_title("Proportion of Missing Data Across 16 Monitoring Stations\n(CTDI Fig. 9 - Seaborn / Matplotlib Style)", fontsize=13, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig("scratch/test_fig9_aligned.png", dpi=200)
plt.close()
print("Fig 9 aligned callouts generated.")

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

# Seaborn theme
sns.set_theme(style="white")
palette = sns.color_palette("tab20", len(st))

fig, ax = plt.subplots(figsize=(12, 9))

wedges, _ = ax.pie(
    st['pct'],
    colors=palette,
    startangle=140,
    wedgeprops=dict(edgecolor="white", linewidth=1.2)
)

# Callout labels
bbox_props = dict(boxstyle="square,pad=0.2", fc="w", ec="#ccc", lw=0.6)
kw = dict(arrowprops=dict(arrowstyle="-", color="#555", lw=0.8), bbox=bbox_props, zorder=3, va="center")

for i, p in enumerate(wedges):
    ang = (p.theta2 - p.theta1)/2. + p.theta1
    y = np.sin(np.deg2rad(ang))
    x = np.cos(np.deg2rad(ang))
    horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
    connectionstyle = f"angle,angle1=0,angle2={ang}"
    kw["arrowprops"].update({"connectionstyle": connectionstyle})
    
    row = st.iloc[i]
    label_text = f"{row['station_name']}: {row['pct']:.2f}%\n({row['missing']:,})"
    
    # Push x outward, y scaled
    ax.annotate(label_text, xy=(x, y), xytext=(1.3 * np.sign(x), 1.25 * y),
                horizontalalignment=horizontalalignment, fontsize=8, **kw)

ax.set_title("Proportion of Missing Data Across 16 Monitoring Stations (CTDI Fig. 9)", fontsize=13, fontweight="bold", pad=25)
plt.subplots_adjust(left=0.15, right=0.85, top=0.9, bottom=0.1)
plt.savefig("scratch/test_fig9_callout.png", dpi=200)
plt.close()
print("Fig 9 callout generated.")

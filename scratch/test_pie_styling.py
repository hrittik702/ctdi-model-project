import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# Load dataset
df = pd.read_csv('data/raw/air_quality/epd_air_quality_2019_2021_hourly.csv')
CRITERIA = ['pm25', 'pm10', 'no2', 'so2', 'o3']
df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
df['missing'] = df[CRITERIA].isna().sum(axis=1)
total_missing = df['missing'].sum()

# Seaborn default styling
sns.set_theme(style="white")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 9,
    "axes.titlesize": 12,
})

# =========================================================================
# Fig 8: Criteria Pollutants (5 categories)
# =========================================================================
fig8_data = []
pollutant_labels = {
    "pm25": "PM2.5", "pm10": "PM10", "no2": "NO2", "so2": "SO2", "o3": "O3"
}
for p in CRITERIA:
    cnt = df[p].isna().sum()
    fig8_data.append({
        "pollutant": pollutant_labels[p],
        "count": cnt,
        "pct": cnt / total_missing * 100
    })
fig8_df = pd.DataFrame(fig8_data)

fig, ax = plt.subplots(figsize=(8, 7))
colors8 = sns.color_palette("deep", len(fig8_df))

# Standard matplotlib/seaborn pie chart: solid pie, labels & percentages directly placed
labels_fig8 = [f"{r.pollutant}\n{r.pct:.2f}%\n({r['count']:,})" for _, r in fig8_df.iterrows()]

wedges, texts = ax.pie(
    fig8_df['pct'],
    labels=labels_fig8,
    colors=colors8,
    startangle=90,
    wedgeprops=dict(edgecolor="white", linewidth=1.5),
    textprops=dict(fontsize=10.5, fontweight="semibold", va="center"),
    labeldistance=1.12
)

ax.set_title("Proportion of Different Pollutants in Total Missing Data\n(CTDI Fig. 8 - Seaborn / Matplotlib Style)", fontsize=12, fontweight="bold", pad=15)
plt.tight_layout()
plt.savefig("scratch/fig_08_seaborn_pie.png", dpi=200)
plt.close()
print("Fig 8 generated.")

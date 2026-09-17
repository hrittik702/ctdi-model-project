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
fig, ax = plt.subplots(figsize=(10, 8))
palette = sns.color_palette("tab20", 24)

labels = [f"{h:02d}:00\n{p:.1f}%" for h, p in zip(h_df['hour'], h_df['pct'])]

wedges, texts = ax.pie(
    h_df['pct'],
    labels=labels,
    colors=palette,
    startangle=90,
    counterclock=False,
    wedgeprops=dict(edgecolor="white", linewidth=1.0),
    labeldistance=1.1,
    textprops=dict(fontsize=8)
)
ax.set_title("Proportion of Hourly Missing Data in Total Missing Data (CTDI Fig. 7)", fontsize=12, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig("scratch/test_fig7_raw.png", dpi=200)
plt.close()
print("Fig 7 raw saved.")

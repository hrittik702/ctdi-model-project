import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# Load data
df = pd.read_csv('data/raw/air_quality/epd_air_quality_2019_2021_hourly.csv')
CRITERIA = ['pm25', 'pm10', 'no2', 'so2', 'o3']
df['missing'] = df[CRITERIA].isna().sum(axis=1)
total_missing = df['missing'].sum()

# 1. Figure 8 (Pollutants)
fig8_data = []
for p in CRITERIA:
    cnt = df[p].isna().sum()
    fig8_data.append({'pollutant': p.upper(), 'count': cnt, 'pct': cnt / total_missing * 100})
fig8_df = pd.DataFrame(fig8_data)

# Seaborn theme
sns.set_theme(style="white", font="sans-serif")
palette8 = sns.color_palette("deep", len(fig8_df))

fig, ax = plt.subplots(figsize=(8, 7))
labels8 = [f"{row.pollutant}\n{row.pct:.2f}%\n({row['count']:,})" for _, row in fig8_df.iterrows()]

wedges, texts, autotexts = ax.pie(
    fig8_df['pct'],
    labels=[row.pollutant for _, row in fig8_df.iterrows()],
    autopct='%1.2f%%',
    pctdistance=0.6,
    labeldistance=1.1,
    colors=palette8,
    startangle=90,
    wedgeprops=dict(edgecolor="white", linewidth=1.5),
    textprops=dict(fontsize=11, fontweight="bold")
)
for at in autotexts:
    at.set_fontsize(10)
    at.set_color("white")
    at.set_weight("bold")

ax.set_title("Proportion of Different Pollutants in Total Missing Data\n(CTDI Fig. 8)", fontsize=13, fontweight="bold", pad=15)
plt.tight_layout()
plt.savefig("scratch/test_fig8.png", dpi=200)
plt.close()
print("Fig 8 generated.")

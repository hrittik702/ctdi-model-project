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
fig, ax = plt.subplots(figsize=(10, 8))
palette = sns.color_palette("tab20", 16)

labels = [f"{r['station_name']}\n{r['pct']:.1f}% ({r['missing']:,})" for _, r in st.iterrows()]

wedges, texts = ax.pie(
    st['pct'],
    labels=labels,
    colors=palette,
    startangle=90,
    wedgeprops=dict(edgecolor="white", linewidth=1.2),
    labeldistance=1.1,
    textprops=dict(fontsize=8)
)
ax.set_title("Proportion of Missing Data Across 16 Monitoring Stations (CTDI Fig. 9)", fontsize=12, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig("scratch/test_fig9_raw.png", dpi=200)
plt.close()
print("Fig 9 raw saved.")

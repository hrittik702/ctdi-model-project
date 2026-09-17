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

sns.set_theme(style="white", font="sans-serif")
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(27, 9))

# -------------------------------------------------------------------------
# Panel 1: Fig 7 Diurnal
# -------------------------------------------------------------------------
h_df = df.groupby('hour')['missing'].sum().reset_index()
h_df['pct'] = h_df['missing'] / total_missing * 100
palette7 = sns.color_palette("tab20", 20) + sns.color_palette("tab20b", 4)

wedges1, _ = ax1.pie(
    h_df['pct'],
    colors=palette7,
    startangle=90,
    counterclock=False,
    wedgeprops=dict(edgecolor="white", linewidth=1.0)
)

for i, p in enumerate(wedges1):
    ang = (p.theta2 - p.theta1) / 2.0 + p.theta1
    rad = np.deg2rad(ang)
    x = np.cos(rad)
    y = np.sin(rad)
    row = h_df.iloc[i]
    h = int(row['hour'])
    pct = row['pct']
    cnt = int(row['missing'])
    
    if pct < 3.2:
        tier = h % 3
        dist = 1.10 if tier == 0 else (1.24 if tier == 1 else 1.38)
        if dist > 1.12:
            ax1.plot([x * 1.01, x * (dist - 0.03)], [y * 1.01, y * (dist - 0.03)], color="#888", lw=0.6)
    elif pct < 5.0:
        dist = 1.12
    else:
        dist = 1.14
        
    if abs(x) < 0.25:
        ha = "center"
        va = "bottom" if y > 0 else "top"
    else:
        ha = "left" if x > 0 else "right"
        va = "center"
    
    label = f"{h:02d}:00\n{pct:.1f}%" if pct < 5.0 else f"{h:02d}:00\n{pct:.1f}% ({cnt:,})"
    ax1.text(x * dist, y * dist, label, ha=ha, va=va, fontsize=7.5, color="#1a202c")

ax1.set_xlim(-1.6, 1.6)
ax1.set_ylim(-1.6, 1.6)
ax1.set_title("(A) Diurnal Missingness Proportion (CTDI Fig. 7)", fontsize=12, fontweight="bold", pad=15)

# -------------------------------------------------------------------------
# Panel 2: Fig 8 Pollutants
# -------------------------------------------------------------------------
fig8_data = []
pollutant_display = {
    "pm25": "PM2.5", "pm10": "PM10", "no2": "NO2", "so2": "SO2", "o3": "O3"
}
for p in CRITERIA:
    cnt = df[p].isna().sum()
    fig8_data.append({"pollutant": pollutant_display[p], "count": cnt, "pct": cnt / total_missing * 100})
fig8_df = pd.DataFrame(fig8_data)
palette8 = sns.color_palette("deep", len(fig8_df))

wedges2, texts2, autotexts2 = ax2.pie(
    fig8_df['pct'],
    labels=fig8_df['pollutant'],
    autopct=lambda p: f"{p:.2f}%\n({int(round(p * total_missing / 100)):,})",
    pctdistance=0.60,
    labeldistance=1.12,
    colors=palette8,
    startangle=90,
    wedgeprops=dict(edgecolor="white", linewidth=1.5),
    textprops=dict(fontsize=11, fontweight="bold", color="#1a202c")
)
for at in autotexts2:
    at.set_fontsize(9.5)
    at.set_color("white")
    at.set_weight("bold")

ax2.set_title("(B) Criteria Pollutant Distribution (CTDI Fig. 8)", fontsize=12, fontweight="bold", pad=15)

# -------------------------------------------------------------------------
# Panel 3: Fig 9 Stations
# -------------------------------------------------------------------------
st = df.groupby('station_name')['missing'].sum().reset_index()
st['pct'] = st['missing'] / total_missing * 100
st = st.sort_values('pct', ascending=False).reset_index(drop=True)
palette9 = sns.color_palette("tab20", 16)

wedges3, _ = ax3.pie(
    st['pct'],
    colors=palette9,
    startangle=90,
    counterclock=False,
    wedgeprops=dict(edgecolor="white", linewidth=1.1)
)

for i, p in enumerate(wedges3):
    ang = (p.theta2 - p.theta1) / 2.0 + p.theta1
    rad = np.deg2rad(ang)
    x = np.cos(rad)
    y = np.sin(rad)
    row = st.iloc[i]
    pct = row['pct']
    cnt = int(row['missing'])
    name = row['station_name']
    
    if pct < 5.0:
        dist = 1.25 if (i % 2 == 1) else 1.10
        if dist > 1.12:
            ax3.plot([x * 1.01, x * (dist - 0.04)], [y * 1.01, y * (dist - 0.04)], color="#888", lw=0.6)
    else:
        dist = 1.12
        
    ha = "left" if x >= 0 else "right"
    va = "center"
    label = f"{name}\n{pct:.1f}% ({cnt:,})"
    ax3.text(x * dist, y * dist, label, ha=ha, va=va, fontsize=7.5, color="#1a202c")

ax3.set_xlim(-1.5, 1.5)
ax3.set_ylim(-1.5, 1.5)
ax3.set_title("(C) Monitoring Station Distribution (CTDI Fig. 9)", fontsize=12, fontweight="bold", pad=15)

fig.suptitle("Hong Kong Air Quality Empirical Missing Data Proportions (2019–2021) — CTDI Figures 7, 8, & 9 Pie Chart Suite", fontsize=14, fontweight="bold", y=0.98)
plt.subplots_adjust(top=0.90, bottom=0.08, left=0.04, right=0.96, wspace=0.22)
plt.savefig("scratch/fig_composite_test.png", dpi=200)
plt.close()
print("Composite generated.")

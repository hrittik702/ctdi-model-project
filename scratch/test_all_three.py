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

# Seaborn theme
sns.set_theme(style="white", font="sans-serif")
plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 13,
})

# =========================================================================
# 1. Figure 7: 24-Hour Diurnal Pie Chart
# =========================================================================
h_df = df.groupby('hour')['missing'].sum().reset_index()
h_df['pct'] = h_df['missing'] / total_missing * 100

fig, ax = plt.subplots(figsize=(12, 10))
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
    
    # 3-tier radial stagger for small crowded slices (pct < 3.5%)
    if pct < 3.2:
        tier = h % 3
        dist = 1.10 if tier == 0 else (1.24 if tier == 1 else 1.38)
        if dist > 1.12:
            ax.plot([x * 1.01, x * (dist - 0.04)], [y * 1.01, y * (dist - 0.04)], color="#888", lw=0.6)
    elif pct < 5.0:
        dist = 1.12
    else:
        dist = 1.14
        
    ha = "left" if x >= 0 else "right"
    va = "center"
    
    if pct >= 5.0:
        label = f"{h:02d}:00\n{pct:.2f}%\n({cnt:,})"
    else:
        label = f"{h:02d}:00\n{pct:.2f}% ({cnt:,})"
    
    ax.text(
        x * dist, y * dist,
        label,
        ha=ha, va=va,
        fontsize=8,
        color="#1a202c",
        fontweight="medium"
    )

ax.set_title("Proportion of Hourly Missing Data in Total Missing Data (CTDI Fig. 7)\n(Seaborn / Matplotlib Style)", fontsize=13, fontweight="bold", pad=25)
plt.tight_layout()
plt.savefig("scratch/fig7_final_test.png", dpi=200)
plt.close()

# =========================================================================
# 2. Figure 8: Criteria Pollutants Pie Chart
# =========================================================================
fig8_data = []
pollutant_display = {
    "pm25": "PM2.5", "pm10": "PM10", "no2": "NO2", "so2": "SO2", "o3": "O3"
}
for p in CRITERIA:
    cnt = df[p].isna().sum()
    fig8_data.append({
        "pollutant": pollutant_display[p],
        "count": cnt,
        "pct": cnt / total_missing * 100
    })
fig8_df = pd.DataFrame(fig8_data)

fig, ax = plt.subplots(figsize=(8.5, 7.5))
palette8 = sns.color_palette("deep", len(fig8_df))

wedges8, texts8, autotexts8 = ax.pie(
    fig8_df['pct'],
    labels=fig8_df['pollutant'],
    autopct=lambda p: f"{p:.2f}%\n({int(round(p * total_missing / 100)):,})",
    pctdistance=0.62,
    labeldistance=1.12,
    colors=palette8,
    startangle=90,
    wedgeprops=dict(edgecolor="white", linewidth=1.5),
    textprops=dict(fontsize=11.5, fontweight="bold", color="#1a202c")
)
for at in autotexts8:
    at.set_fontsize(10)
    at.set_color("white")
    at.set_weight("bold")

ax.set_title("Proportion of Different Pollutants in Total Missing Data (CTDI Fig. 8)\n(Seaborn / Matplotlib Style)", fontsize=13, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig("scratch/fig8_final_test.png", dpi=200)
plt.close()

# =========================================================================
# 3. Figure 9: 16 Monitoring Stations Pie Chart
# =========================================================================
st = df.groupby('station_name')['missing'].sum().reset_index()
st['pct'] = st['missing'] / total_missing * 100
st = st.sort_values('pct', ascending=False).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(12, 10))
palette9 = sns.color_palette("tab20", 16)

wedges9, _ = ax.pie(
    st['pct'],
    colors=palette9,
    startangle=90,
    counterclock=False,
    wedgeprops=dict(edgecolor="white", linewidth=1.2)
)

for i, p in enumerate(wedges9):
    ang = (p.theta2 - p.theta1) / 2.0 + p.theta1
    rad = np.deg2rad(ang)
    x = np.cos(rad)
    y = np.sin(rad)
    row = st.iloc[i]
    pct = row['pct']
    cnt = int(row['missing'])
    name = row['station_name']
    
    # Stagger for smaller stations (< 5.0%)
    if pct < 5.0:
        dist = 1.25 if (i % 2 == 1) else 1.10
        if dist > 1.12:
            ax.plot([x * 1.01, x * (dist - 0.04)], [y * 1.01, y * (dist - 0.04)], color="#888", lw=0.6)
    else:
        dist = 1.12
        
    ha = "left" if x >= 0 else "right"
    va = "center"
    
    label = f"{name}\n{pct:.2f}% ({cnt:,})"
    
    ax.text(
        x * dist, y * dist,
        label,
        ha=ha, va=va,
        fontsize=8.5,
        color="#1a202c",
        fontweight="medium"
    )

ax.set_title("Proportion of Missing Data Across 16 Monitoring Stations (CTDI Fig. 9)\n(Seaborn / Matplotlib Style)", fontsize=13, fontweight="bold", pad=25)
plt.tight_layout()
plt.savefig("scratch/fig9_final_test.png", dpi=200)
plt.close()
print("All three test figures generated successfully.")

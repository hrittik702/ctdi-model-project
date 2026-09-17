import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "air_quality" / "epd_air_quality_2019_2021_hourly.csv"
SCRATCH_DIR = PROJECT_ROOT / "scratch" / "test_unbloated"
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

# Load data
df_aq = pd.read_csv(DATA_PATH)
CRITERIA = ["pm25", "pm10", "no2", "so2", "o3"]
POLLUTANT_DISPLAY = {
    "pm25": "PM2.5",
    "pm10": "PM10",
    "no2": "NO2",
    "so2": "SO2",
    "o3": "O3"
}

df_aq["hour"] = pd.to_datetime(df_aq["timestamp"]).dt.hour
df_aq["missing_count"] = df_aq[CRITERIA].isna().sum(axis=1)
total_missing = df_aq["missing_count"].sum()

# Theme: clean, simple
sns.set_theme(style="white", font="sans-serif")
plt.rcParams.update({
    "font.size": 9.5,
    "axes.titlesize": 13,
})

# ===========================================================================
# 1. Figure 7: Diurnal
# ===========================================================================
fig7_summary = df_aq.groupby("hour")["missing_count"].sum().reset_index()
fig7_summary["prop"] = (fig7_summary["missing_count"] / total_missing) * 100

fig, ax = plt.subplots(figsize=(11, 10))
palette7 = sns.color_palette("tab20", 20) + sns.color_palette("tab20b", 4)

wedges7, _ = ax.pie(
    fig7_summary["prop"],
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
    row = fig7_summary.iloc[i]
    h = int(row["hour"])
    pct = round(row["prop"], 1)
    
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
        
    if abs(x) < 0.25:
        ha = "center"
        va = "bottom" if y > 0 else "top"
    else:
        ha = "left" if x > 0 else "right"
        va = "center"
    
    label = f"{h:02d}:00\n{pct:.1f}%"
    ax.text(
        x * dist, y * dist,
        label,
        ha=ha, va=va,
        fontsize=9,
        color="#1a202c"
    )

ax.set_xlim(-1.55, 1.55)
ax.set_ylim(-1.55, 1.55)
ax.set_title("Hourly Distribution of Missing Air Quality Data", fontsize=14, fontweight="bold", pad=20)
plt.tight_layout()
fig7_path = SCRATCH_DIR / "fig7.png"
plt.savefig(fig7_path, dpi=300)
plt.close()

# ===========================================================================
# 2. Figure 8: Pollutants
# ===========================================================================
fig8_data = []
for p in CRITERIA:
    cnt = int(df_aq[p].isna().sum())
    fig8_data.append({
        "pollutant": POLLUTANT_DISPLAY[p],
        "prop": cnt / total_missing * 100
    })
fig8_df = pd.DataFrame(fig8_data)

fig, ax = plt.subplots(figsize=(8, 7))
palette8 = sns.color_palette("deep", len(fig8_df))

wedges8, texts8, autotexts8 = ax.pie(
    fig8_df["prop"],
    labels=fig8_df["pollutant"],
    autopct=lambda p: f"{p:.1f}%",
    pctdistance=0.62,
    labeldistance=1.12,
    colors=palette8,
    startangle=90,
    wedgeprops=dict(edgecolor="white", linewidth=1.5),
    textprops=dict(fontsize=12, fontweight="bold", color="#1a202c")
)
for at in autotexts8:
    at.set_fontsize(12)
    at.set_color("white")
    at.set_weight("bold")

ax.set_title("Distribution of Missing Data by Air Pollutant", fontsize=14, fontweight="bold", pad=20)
plt.tight_layout()
fig8_path = SCRATCH_DIR / "fig8.png"
plt.savefig(fig8_path, dpi=300)
plt.close()

# ===========================================================================
# 3. Figure 9: Stations
# ===========================================================================
fig9_summary = df_aq.groupby(["station_id", "station_name"])["missing_count"].sum().reset_index()
fig9_summary["prop"] = fig9_summary["missing_count"] / total_missing * 100
fig9_summary = fig9_summary.sort_values("prop", ascending=False).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(11, 10))
palette9 = sns.color_palette("tab20", 16)

wedges9, _ = ax.pie(
    fig9_summary["prop"],
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
    row = fig9_summary.iloc[i]
    pct = round(row["prop"], 1)
    name = row["station_name"]
    
    if pct < 5.0:
        dist = 1.25 if (i % 2 == 1) else 1.10
        if dist > 1.12:
            ax.plot([x * 1.01, x * (dist - 0.04)], [y * 1.01, y * (dist - 0.04)], color="#888", lw=0.6)
    else:
        dist = 1.12
        
    ha = "left" if x >= 0 else "right"
    va = "center"
    label = f"{name}\n{pct:.1f}%"
    ax.text(
        x * dist, y * dist,
        label,
        ha=ha, va=va,
        fontsize=9,
        color="#1a202c"
    )

ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_title("Distribution of Missing Data Across Monitoring Stations", fontsize=14, fontweight="bold", pad=20)
plt.tight_layout()
fig9_path = SCRATCH_DIR / "fig9.png"
plt.savefig(fig9_path, dpi=300)
plt.close()

# ===========================================================================
# 4. Composite
# ===========================================================================
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(25, 8))

# Panel 1: Fig 7 Diurnal
wedges1, _ = ax1.pie(
    fig7_summary["prop"],
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
    row = fig7_summary.iloc[i]
    h = int(row["hour"])
    pct = round(row["prop"], 1)
    
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
    
    label = f"{h:02d}:00\n{pct:.1f}%"
    ax1.text(x * dist, y * dist, label, ha=ha, va=va, fontsize=8, color="#1a202c")

ax1.set_xlim(-1.55, 1.55)
ax1.set_ylim(-1.55, 1.55)
ax1.set_title("Hourly Distribution", fontsize=13, fontweight="bold", pad=15)

# Panel 2: Fig 8 Pollutants
wedges2, texts2, autotexts2 = ax2.pie(
    fig8_df["prop"],
    labels=fig8_df["pollutant"],
    autopct=lambda p: f"{p:.1f}%",
    pctdistance=0.60,
    labeldistance=1.12,
    colors=palette8,
    startangle=90,
    wedgeprops=dict(edgecolor="white", linewidth=1.5),
    textprops=dict(fontsize=11.5, fontweight="bold", color="#1a202c")
)
for at in autotexts2:
    at.set_fontsize(11)
    at.set_color("white")
    at.set_weight("bold")

ax2.set_title("Pollutant Distribution", fontsize=13, fontweight="bold", pad=15)

# Panel 3: Fig 9 Stations
wedges3, _ = ax3.pie(
    fig9_summary["prop"],
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
    row = fig9_summary.iloc[i]
    pct = round(row["prop"], 1)
    name = row["station_name"]
    
    if pct < 5.0:
        dist = 1.25 if (i % 2 == 1) else 1.10
        if dist > 1.12:
            ax3.plot([x * 1.01, x * (dist - 0.04)], [y * 1.01, y * (dist - 0.04)], color="#888", lw=0.6)
    else:
        dist = 1.12
        
    ha = "left" if x >= 0 else "right"
    va = "center"
    label = f"{name}\n{pct:.1f}%"
    ax3.text(x * dist, y * dist, label, ha=ha, va=va, fontsize=8, color="#1a202c")

ax3.set_xlim(-1.5, 1.5)
ax3.set_ylim(-1.5, 1.5)
ax3.set_title("Spatial Distribution (16 Stations)", fontsize=13, fontweight="bold", pad=15)

fig.suptitle("Empirical Missing Air Quality Data Distributions (2019–2021)", fontsize=15, fontweight="bold", y=0.98)
plt.subplots_adjust(top=0.88, bottom=0.08, left=0.04, right=0.96, wspace=0.22)
comp_path = SCRATCH_DIR / "composite.png"
plt.savefig(comp_path, dpi=300)
plt.close()

print("All unbloated test figures generated successfully!")

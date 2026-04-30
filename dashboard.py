import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("Set2")

# ── Load Data ──────────────────────────────────────────────────────────────────
df_day  = pd.read_csv("main_data.csv")
df_hour = pd.read_csv("hour.csv")

df_day['dteday']  = pd.to_datetime(df_day['dteday'])
df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])

season_map     = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
weather_map    = {1: 'Clear', 2: 'Mist', 3: 'Light Snow/Rain', 4: 'Heavy Rain'}
workingday_map = {0: 'Non-Working Day', 1: 'Working Day'}

for df in [df_day, df_hour]:
    df['season_label']     = df['season'].map(season_map)
    df['weathersit_label'] = df['weathersit'].map(weather_map)
    df['workingday_label'] = df['workingday'].map(workingday_map)

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.title("Filter Data")

min_date = df_day['dteday'].min()
max_date = df_day['dteday'].max()

start_date, end_date = st.sidebar.date_input(
    "Rentang Tanggal",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

selected_season = st.sidebar.multiselect(
    "Musim",
    options=['Spring', 'Summer', 'Fall', 'Winter'],
    default=['Spring', 'Summer', 'Fall', 'Winter']
)

# ── Filter ─────────────────────────────────────────────────────────────────────
df_day_filtered = df_day[
    (df_day['dteday'] >= pd.to_datetime(start_date)) &
    (df_day['dteday'] <= pd.to_datetime(end_date)) &
    (df_day['season_label'].isin(selected_season))
]

df_hour_filtered = df_hour[
    (df_hour['dteday'] >= pd.to_datetime(start_date)) &
    (df_hour['dteday'] <= pd.to_datetime(end_date))
]

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🚲 Dashboard Analisis Penyewaan Sepeda")
st.markdown("Sumber data: Bike Sharing Dataset (2011–2012)")
st.markdown("---")

# ── Metric Cards ───────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Total Penyewaan", f"{df_day_filtered['cnt'].sum():,.0f}")
col2.metric("Rata-rata Harian", f"{df_day_filtered['cnt'].mean():,.0f}")
col3.metric("Penyewaan Tertinggi", f"{df_day_filtered['cnt'].max():,.0f}")

st.markdown("---")

# ── Visualisasi 1: Musim & Cuaca ───────────────────────────────────────────────
st.subheader("Pertanyaan 1: Pengaruh Musim & Cuaca terhadap Penyewaan Harian")

season_avg  = df_day_filtered.groupby('season_label')['cnt'].mean().reset_index()
season_avg.columns = ['Musim', 'Rata-rata Penyewaan']
season_avg  = season_avg.sort_values('Rata-rata Penyewaan', ascending=False)

weather_avg = df_day_filtered.groupby('weathersit_label')['cnt'].mean().reset_index()
weather_avg.columns = ['Cuaca', 'Rata-rata Penyewaan']
weather_avg = weather_avg.sort_values('Rata-rata Penyewaan', ascending=False)

fig1, axes = plt.subplots(1, 2, figsize=(14, 5))

sns.barplot(data=season_avg, x='Musim', y='Rata-rata Penyewaan',
            order=season_avg['Musim'], ax=axes[0], palette='Set2')
axes[0].set_title('Rata-rata Penyewaan per Musim', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Musim')
axes[0].set_ylabel('Rata-rata Jumlah Penyewaan')
for bar in axes[0].patches:
    axes[0].annotate(f'{bar.get_height():.0f}',
                     (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     ha='center', va='bottom', fontsize=9)

sns.barplot(data=weather_avg, x='Cuaca', y='Rata-rata Penyewaan',
            order=weather_avg['Cuaca'], ax=axes[1], palette='Set1')
axes[1].set_title('Rata-rata Penyewaan per Kondisi Cuaca', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Kondisi Cuaca')
axes[1].set_ylabel('Rata-rata Jumlah Penyewaan')
axes[1].tick_params(axis='x', labelrotation=15)
for bar in axes[1].patches:
    axes[1].annotate(f'{bar.get_height():.0f}',
                     (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     ha='center', va='bottom', fontsize=9)

plt.tight_layout()
st.pyplot(fig1)

with st.expander("📌 Insight Pertanyaan 1"):
    st.write("""
    - Musim **Fall** mencatat rata-rata penyewaan tertinggi, diikuti **Summer** dan **Winter**.
    - Cuaca **Clear** menghasilkan penyewaan jauh lebih tinggi dibanding cuaca buruk.
    - Cuaca **Light Snow/Rain** menurunkan penyewaan secara signifikan.
    """)

st.markdown("---")

# ── Visualisasi 2: Pola Per Jam ─────────────────────────────────────────────
st.subheader("Pertanyaan 2: Pola Penyewaan per Jam (Hari Kerja vs Hari Libur)")

hour_avg     = df_hour_filtered.groupby('hr')['cnt'].mean().reset_index()
hour_avg.columns = ['Jam', 'Rata-rata Penyewaan']

hour_workday = df_hour_filtered.groupby(['hr', 'workingday_label'])['cnt'].mean().reset_index()
hour_workday.columns = ['Jam', 'Tipe Hari', 'Rata-rata Penyewaan']

fig2, axes2 = plt.subplots(2, 1, figsize=(14, 10))

sns.lineplot(data=hour_avg, x='Jam', y='Rata-rata Penyewaan',
             ax=axes2[0], color='steelblue', linewidth=2.5, marker='o', markersize=5)
axes2[0].set_title('Rata-rata Penyewaan per Jam (Keseluruhan)', fontsize=12, fontweight='bold')
axes2[0].set_xlabel('Jam')
axes2[0].set_ylabel('Rata-rata Jumlah Penyewaan')
axes2[0].set_xticks(range(0, 24))

peak_hour = hour_avg.loc[hour_avg['Rata-rata Penyewaan'].idxmax()]
axes2[0].annotate(f"Puncak: Jam {int(peak_hour['Jam'])}",
                  xy=(peak_hour['Jam'], peak_hour['Rata-rata Penyewaan']),
                  xytext=(peak_hour['Jam'] + 1.5, peak_hour['Rata-rata Penyewaan'] - 10),
                  arrowprops=dict(arrowstyle='->', color='red'),
                  fontsize=10, color='red')

sns.lineplot(data=hour_workday, x='Jam', y='Rata-rata Penyewaan',
             hue='Tipe Hari', ax=axes2[1], linewidth=2.5, marker='o', markersize=5)
axes2[1].set_title('Perbandingan Penyewaan per Jam: Hari Kerja vs Hari Libur',
                   fontsize=12, fontweight='bold')
axes2[1].set_xlabel('Jam')
axes2[1].set_ylabel('Rata-rata Jumlah Penyewaan')
axes2[1].set_xticks(range(0, 24))
axes2[1].legend(title='Tipe Hari')

plt.tight_layout()
st.pyplot(fig2)

with st.expander("📌 Insight Pertanyaan 2"):
    st.write("""
    - Puncak penyewaan terjadi pada jam **08.00** dan **17.00–18.00**, mengikuti pola commuting.
    - Pada **hari kerja**, pola bimodal (pagi & sore) sangat jelas.
    - Pada **hari libur**, penyewaan lebih merata di siang hari (10.00–15.00).
    """)

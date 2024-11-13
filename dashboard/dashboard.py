import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style='dark')

def create_monthly_sharing_df(df):
    monthly_sharing_df = all_df[(all_df["yr_x"] == 1) & (all_df["mnth_x"] >= 1) & (all_df["mnth_x"] <= 5)].groupby(
        by=["mnth_x"]).agg({
        "registered_x": ["sum"]
    })
    monthly_sharing_df.rename(columns={"registered_x": "total"}, inplace=True)
    monthly_sharing_df = monthly_sharing_df.reset_index()

    # Melakukan mapping untuk mengganti nilai kolom "mnth_x" menjadi nama bulannya
    monthly_sharing_df["mnth_x"] = monthly_sharing_df["mnth_x"].map(
        {1: "January", 2: "February", 3: "March", 4: "April", 5: "May"})

    return monthly_sharing_df

def create_seasons_sharing_df(df):
    seasons_sharing_df = all_df[all_df["yr_x"] == 0].groupby(by=["season_x"]).agg({
        "cnt_x": "sum"
    }).sort_values(by="cnt_x", ascending=False)
    seasons_sharing_df.rename(columns={"cnt_x": "total_sharing"}, inplace=True)

    # Melakukan reset index pada dataframe
    seasons_sharing_df = seasons_sharing_df.reset_index(drop=False)

    # Melakukan mapping untuk mengganti nilai kolom "season_x" menjadi nama musimnya
    seasons_sharing_df["season_x"] = seasons_sharing_df["season_x"].map(
        {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"})

    return seasons_sharing_df

def create_cluster_df(df):
    avg_per_hour = all_df.groupby("hr")["cnt_x"].mean().reset_index()

    # Menentukan threshold menggunakan median
    threshold = avg_per_hour["cnt_x"].median()

    # Menambahkan kolom baru "category" untuk mengelompokkan jam sibuk dan jam tenang
    avg_per_hour["category"] = avg_per_hour["cnt_x"].apply(lambda x: "Peak Hours" if x > threshold else "Quiet Hours")

    # Menyimpan hasil pengelompokkan ke dalam jam_sibuk dan jam_tenang
    jam_sibuk = avg_per_hour[avg_per_hour["category"] == "Peak Hours"]
    jam_tenang = avg_per_hour[avg_per_hour["category"] == "Quiet Hours"]

    # Menyimpan data jamnya ke dalam avg_per_hour_grouped
    cluster_grouped = avg_per_hour.groupby("category")["hr"].apply(lambda x: ', '.join(map(str, x))).reset_index()

    return avg_per_hour, threshold, cluster_grouped

# Membaca data dari all_data.csv
all_df = pd.read_csv("./dashboard/all_data.csv")

# Membuat komponen filter menggunakan dteday_x
all_df["dteday_x"] = pd.to_datetime(all_df["dteday_x"])
min_date = all_df["dteday_x"].min()
max_date = all_df["dteday_x"].max()

# Membuat sidebar untuk memilih rentang waktu
with st.sidebar:
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Menyimpan data yang di-filter ke main_df
main_df = all_df[(all_df["dteday_x"] >= str(start_date)) &
                (all_df["dteday_x"] <= str(end_date))]

# Memanggil helper function
monthly_sharing_df = create_monthly_sharing_df(main_df)
seasons_sharing_df = create_seasons_sharing_df(main_df)
cluster_df, threshold, cluster_grouped = create_cluster_df(main_df)

# Judul dashboard
st.header("Bike Sharing Dashboard :sparkles:")
# Mencetak data penyewaan sepeda oleh pengguna terdaftar, kasual, dan keseluruhan
st.subheader("Daily Sharings")
col1, col2, col3 = st.columns(3)

with col1:
    total_registered = all_df.registered_x.sum()
    st.metric("Total Registered Sharings", value=total_registered)

with col2:
    total_casual = all_df.casual_x.sum()
    st.metric("Total Casual Sharings", value=total_casual)

with col3:
    total_sharings = all_df.cnt_x.sum()
    st.metric("Total Sharings", value=total_sharings)
# Menampilkan visualisasi data penyewaan harian
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    all_df["dteday_x"],
    all_df["cnt_x"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

# Menampilkan visualisasi data penyewaan per jam berdasarkan musim pada 2011
st.subheader("Hourly Bike Sharing by Seasons at 2011")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="season_x", y="total_sharing", data=seasons_sharing_df, palette=colors, ax=ax[0], hue="season_x")
ax[0].set_ylabel("Total Bike Sharing")
ax[0].set_xlabel("Season")
ax[0].set_title("Seasons With Most Bike Sharing per Hour", loc="center", fontsize=15)
ax[0].tick_params(axis ="y", labelsize=12)

sns.barplot(x="season_x", y="total_sharing", data=seasons_sharing_df.sort_values(by="total_sharing", ascending=True), palette=colors, ax=ax[1], hue="season_x")
ax[1].set_ylabel("Total Bike Sharing")
ax[1].set_xlabel("Season")
ax[1].set_title("Seasons With Least Bike Sharing per Hour", loc="center", fontsize=15)
ax[1].tick_params(axis ="y", labelsize=12)
st.pyplot(fig)

# Menampilkan visualisasi data penyewaan per hari oleh pengguna terdaftar pada Januari - Mei 2012
st.subheader("Daily Bike Sharing by Registered Users From January to May 2012")

fig = plt.figure(figsize=(10, 5))
plt.plot(monthly_sharing_df["mnth_x"], monthly_sharing_df["total"], marker="o", linewidth=2, color="#72BCD4")
plt.xlabel("Month")
plt.ylabel("Total Bike Sharing")
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
st.pyplot(fig)

# Menampilkan tabel jam sibuk dan jam tenang
st.subheader("Peak Hours and Quiet Hours")
st.dataframe(cluster_grouped)

# Menampilkan visualisasi data rata-rata penyewaan sepeda per jam
st.subheader("Average Bike Sharing per Hour")

fig = plt.figure(figsize=(12, 6))
plt.plot(cluster_df["hr"], cluster_df["cnt_x"], label="Average Bike Sharing")
plt.axhline(y=threshold, color="g", linestyle="--", label=f"Median Threshold ({threshold:.2f})")
plt.xticks(range(0, 24, 1))
plt.xlabel("Hour")
plt.ylabel("Average Bike Sharing")
plt.legend()
st.pyplot(fig)

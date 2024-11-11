import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_monthly_sharing_df(df):
    monthly_sharing_df = all_df[(all_df["yr_x"] == 1) & (all_df["mnth_x"] >= 1) & (all_df["mnth_x"] <= 5)].groupby(
        by=["mnth_x"]).agg({
        "registered_x": ["sum"]
    })
    monthly_sharing_df.rename(columns={"registered_x": "total"}, inplace=True)
    monthly_sharing_df = monthly_sharing_df.reset_index()

    monthly_sharing_df["mnth_x"] = monthly_sharing_df["mnth_x"].map(
        {1: "January", 2: "February", 3: "March", 4: "April", 5: "May"})

    return monthly_sharing_df

def create_seasons_sharing_df(df):
    seasons_sharing_df = all_df[all_df["yr_x"] == 0].groupby(by=["season_x"]).agg({
        "cnt_x": "sum"
    }).sort_values(by="cnt_x", ascending=False)
    seasons_sharing_df.rename(columns={"cnt_x": "total_sharing"}, inplace=True)
    seasons_sharing_df = seasons_sharing_df.reset_index(drop=False)

    seasons_sharing_df["season_x"] = seasons_sharing_df["season_x"].map(
        {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"})

    return seasons_sharing_df

def create_cluster_df(df):
    avg_per_hour = all_df.groupby("hr")["cnt_x"].mean().reset_index()
    threshold = avg_per_hour["cnt_x"].median()
    avg_per_hour["category"] = avg_per_hour["cnt_x"].apply(lambda x: "Jam Sibuk" if x > threshold else "Jam Tenang")

    return avg_per_hour

all_df = pd.read_csv("all_data.csv")

st.title("Bike Sharing Dashboard")
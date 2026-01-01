import streamlit as st
from folium.plugins import FastMarkerCluster
from streamlit_folium import st_folium
import folium as f

import data


def heatmap():
    st.markdown('# 🗺️ USA Unfall-Heatmap')

    df =  data.load_data()

    MAX_POINTS = 50000
    df_good = df.loc[~df["Start_Lat"].isna(), ["Start_Lat", "Start_Lng"]]

    if len(df_good.index) > MAX_POINTS:
        df_good = df_good.sample(MAX_POINTS, random_state=42)


    m = f.Map(location=[df['Start_Lat'].mean(), df['Start_Lng'].mean()], zoom_start=7)

    coordinates = df_good.values.tolist()

    FastMarkerCluster(coordinates).add_to(m)

    st_data = st_folium(m, width=725)
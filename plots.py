import data
import folium as f
from folium.plugins import FastMarkerCluster
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
import plotly.express as px


def heatmap():
    st.markdown('# 🗺️ USA Unfall-Heatmap')

    df = data.load_data()

    MAX_POINTS = 5000
    df_good = df.loc[~df["Start_Lat"].isna(), ["Start_Lat", "Start_Lng"]]

    if len(df_good.index) > MAX_POINTS:
        df_good = df_good.sample(MAX_POINTS, random_state=42)

    m = f.Map(location=[df['Start_Lat'].mean(), df['Start_Lng'].mean()], zoom_start=7)

    coordinates = df_good.values.tolist()

    FastMarkerCluster(coordinates).add_to(m)

    st_data = st_folium(m, width=725)


def hour_of_day(df):
    # ---------- Daten vorbereiten ----------
    df = df.copy()
    df['Start_Time'] = pd.to_datetime(df['Start_Time'], format='mixed')
    df = df[['Start_Time', 'Severity']].dropna()
    df['Hour'] = df['Start_Time'].dt.hour

    hours = range(24)

    # ---------- Alle Unfälle ----------
    hour_all = (
        df.groupby('Hour')
        .size()
        .reindex(hours, fill_value=0)
    )

    # ---------- Schwere Unfälle ----------
    df_severe = df[df['Severity'] >= 3]

    hour_severe = (
        df_severe.groupby('Hour')
        .size()
        .reindex(hours, fill_value=0)
    )

    ymax = max(hour_all.max(), hour_severe.max()) * 1.1

    # ---------- Plot ----------
    st.subheader("Unfälle nach Uhrzeit")

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    axes[0].bar(hour_all.index, hour_all.values)
    axes[0].set_title("Alle Unfälle")
    axes[0].set_ylabel("Anzahl")
    axes[0].set_ylim(0, ymax)

    axes[1].bar(hour_severe.index, hour_severe.values)
    axes[1].set_title("Schwere Unfälle (Severity ≥ 3)")
    axes[1].set_ylabel("Anzahl")
    axes[1].set_xlabel("Hour of Day (0 = Mitternacht)")
    axes[1].set_ylim(0, ymax)

    plt.tight_layout()
    st.pyplot(fig)

    # ---------- Insight berechnen ----------
    night_hours = list(range(22, 24)) + list(range(0, 6))
    day_hours = list(range(6, 22))

    night_share = (
        hour_severe[night_hours].sum() /
        hour_all[night_hours].sum()
        if hour_all[night_hours].sum() > 0 else 0
    )

    day_share = (
        hour_severe[day_hours].sum() /
        hour_all[day_hours].sum()
        if hour_all[day_hours].sum() > 0 else 0
    )

    # ---------- Insight anzeigen ----------
    st.markdown(
        f"### Insight: \nEntgegen der Erwartung ist der Anteil schwerer Unfälle tagsüber höher ({day_share:.1%}) als nachts ({night_share:.1%})."
        "Ein möglicher Grund ist das deutlich höhere Verkehrsaufkommen am Tag."
    )

def weather(df):
    st.subheader("Wetterbedingungen und Unfallschwere")

    # Kopie erstellen und relevante Spalten behalten
    df_weather = df[['Weather_Condition', 'Severity']].dropna().copy()

    # Wetter-Häufigkeit zählen für Gruppierung
    weather_counts = df_weather["Weather_Condition"].value_counts()
    MIN_COUNT = 5000
    
    # Top-Wetterbedingungen identifizieren
    top_weather = weather_counts[weather_counts >= MIN_COUNT].index.tolist()
    
    # "Other" zuweisen
    df_weather['Weather_Grouped'] = df_weather['Weather_Condition'].apply(
        lambda x: x if x in top_weather else 'Other'
    )

    # Daten für den Plot vorbereiten: Zählen pro Wettergruppe und Severity
    weather_severity = (
        df_weather.groupby(['Weather_Grouped', 'Severity'])
        .size()
        .reset_index(name='Count')
    )

    # Plot 1: Absolute Zahlen (Stacked Bar)
    fig1 = px.bar(
        weather_severity,
        x="Weather_Grouped",
        y="Count",
        color="Severity",
        title="Anzahl der Unfälle nach Wetter und Schweregrad",
        labels={"Weather_Grouped": "Wetterbedingung", "Count": "Anzahl der Unfälle", "Severity": "Schweregrad"},
        barmode="stack",
        category_orders={"Severity": [1, 2, 3, 4]}
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Plot 2: Relative Verteilung (100% Stacked Bar)
    # Berechne Prozentsätze innerhalb jeder Wettergruppe
    weather_severity_percent = weather_severity.copy()
    group_sums = weather_severity_percent.groupby('Weather_Grouped')['Count'].transform('sum')
    weather_severity_percent['Percentage'] = (weather_severity_percent['Count'] / group_sums) * 100

    fig2 = px.bar(
        weather_severity_percent,
        x="Weather_Grouped",
        y="Percentage",
        color="Severity",
        title="Relative Verteilung der Unfallschwere nach Wetter",
        labels={"Weather_Grouped": "Wetterbedingung", "Percentage": "Anteil (%)", "Severity": "Schweregrad"},
        barmode="stack",
        category_orders={"Severity": [1, 2, 3, 4]}
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Insight berechnen
    avg_severity_by_weather = df_weather.groupby('Weather_Grouped')['Severity'].mean().sort_values(ascending=False)
    highest_weather = avg_severity_by_weather.index[0]
    highest_val = avg_severity_by_weather.iloc[0]

    st.markdown(
        f"### Insight: \nBei der Wetterbedingung **{highest_weather}** ist die durchschnittliche Unfallschwere am höchsten (**{highest_val:.2f}**)."
    )

def state_analysis(df):
    st.subheader("Unfälle nach Bundesstaaten")
    
    state_counts = df['State'].value_counts().reset_index()
    state_counts.columns = ['State', 'Count']
    
    # Top 15 States
    top_states = state_counts.head(15)
    
    fig = px.bar(
        top_states, 
        x='State', 
        y='Count', 
        title='Top 15 Bundesstaaten mit den meisten Unfällen',
        labels={'State': 'Bundesstaat', 'Count': 'Anzahl der Unfälle'},
        color='Count',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Durchschnittliche Severity pro State (Top 15 nach Anzahl)
    avg_severity_state = df[df['State'].isin(top_states['State'])].groupby('State')['Severity'].mean().reset_index()
    avg_severity_state = avg_severity_state.sort_values('Severity', ascending=False)
    
    fig2 = px.bar(
        avg_severity_state,
        x='State',
        y='Severity',
        title='Durchschnittliche Unfallschwere in den Top 15 Bundesstaaten',
        labels={'State': 'Bundesstaat', 'Severity': 'Durchschnittliche Schwere (1-4)'},
        color='Severity',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig2, use_container_width=True)

def traffic_features(df):
    st.subheader("Einfluss von Verkehrsobjekten")
    
    features = ['Crossing', 'Junction', 'Traffic_Signal']
    feature_data = []
    
    for feature in features:
        # Berechne Anteil schwerer Unfälle (Severity >= 3) wenn Feature True vs False
        for val in [True, False]:
            subset = df[df[feature] == val]
            if len(subset) > 0:
                severe_share = (len(subset[subset['Severity'] >= 3]) / len(subset)) * 100
                feature_data.append({
                    'Feature': feature,
                    'Present': 'Ja' if val else 'Nein',
                    'Severe_Share': severe_share,
                    'Avg_Severity': subset['Severity'].mean()
                })
    
    df_features = pd.DataFrame(feature_data)
    
    fig = px.bar(
        df_features,
        x='Feature',
        y='Severe_Share',
        color='Present',
        barmode='group',
        title='Anteil schwerer Unfälle (Severity ≥ 3) nach Verkehrsobjekt',
        labels={'Severe_Share': 'Anteil schwerer Unfälle (%)', 'Feature': 'Objekt', 'Present': 'Vorhanden'},
        color_discrete_map={'Ja': '#ef553b', 'Nein': '#636efa'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    **Was wir hier sehen:**
    Diese Grafik zeigt, ob Unfälle an bestimmten Stellen (wie Kreuzungen oder Ampeln) tendenziell schwerer ausfallen. 
    Überraschenderweise ist der Anteil schwerer Unfälle an Ampeln (Traffic Signal) oft geringer, da dort meist niedrigere Geschwindigkeiten gefahren werden.
    """)
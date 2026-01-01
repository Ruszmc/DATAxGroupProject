import streamlit as st
import kagglehub
from kagglehub import KaggleDatasetAdapter

@st.cache_data
def load_data():
    file_path = "US_Accidents_March23.csv"

    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "sobhanmoosavi/us-accidents",
        file_path,
        # Spalten filtern
        pandas_kwargs={
            "usecols": [
                "ID",
                "Severity",
                "Start_Time",
                "State",
                "Weather_Condition",
                "Start_Lat",
                "Start_Lng"
            ]
        }
    )

    return df
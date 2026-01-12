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
                "City",
                "Weather_Condition",
                "Start_Lat",
                "Start_Lng",
                "Temperature(F)",
                "Visibility(mi)",
                "Crossing",
                "Junction",
                "Traffic_Signal"
            ]
        }
    )

    # State-Abkürzungen zu vollen Namen mappen
    us_state_to_abbrev = {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
        "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
        "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
        "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
        "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
        "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
        "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
        "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
        "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
        "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
        "DC": "District of Columbia"
    }
    df['State'] = df['State'].map(us_state_to_abbrev).fillna(df['State'])

    return df
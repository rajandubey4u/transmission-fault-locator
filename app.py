import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Transmission Line Fault Locator",
    page_icon="⚡"
)

st.title("⚡ Transmission Line Fault Locator")

# Excel file
FILE = "259-249-250.xlsx"

# Relay configuration
LINES = {
    "L#259": {
        "first": "MTPS",
        "second": "PGCIL"
    },
    "L#250": {
        "first": "MTPS",
        "second": "Ramgarh"
    },
    "L#249": {
        "first": "Ramgarh",
        "second": "PGCIL"
    }
}


@st.cache_data
def load_data():

    data = {}

    for line in LINES:

        df = pd.read_excel(
            FILE,
            sheet_name=line
        )

        # Column E = cumulative distance
        df.iloc[:, 4] = pd.to_numeric(
            df.iloc[:, 4],
            errors="coerce"
        )

        data[line] = df

    return data


data = load_data()


# -----------------------------
# INPUTS
# -----------------------------

line = st.selectbox(
    "Select The Line",
    list(LINES.keys())
)

relay = st.selectbox(
    "Relay Location",
    [
        LINES[line]["first"],
        LINES[line]["second"]
    ]
)

fault_distance = st.number_input(
    "Enter Fault Distance (km)",
    min_value=0.0,
    step=0.1,
    format="%.3f"
)


# -----------------------------
# CALCULATE
# -----------------------------

if st.button("CALCULATE", type="primary"):

    df = data[line]

    cumulative = df.iloc[:, 4]

    total_distance = cumulative.max()

    # Distance measured from first relay
    if relay == LINES[line]["first"]:

        distance_from_first = fault_distance

    else:

        distance_from_first = (
            total_distance - fault_distance
        )

    # Find last cumulative distance
    # less than or equal to fault distance

    valid = df[
        df.iloc[:, 4] <= distance_from_first
    ]

    if len(valid) == 0:

        st.error(
            "Fault distance is outside the available line data."
        )

    else:

        row = valid.iloc[-1]

        st.divider()

        st.subheader("Fault Location")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Location No.",
                str(row.iloc[1])
            )

            st.metric(
                "AP No.",
                str(row.iloc[0])
            )

        with col2:

            st.metric(
                "L# Location",
                str(row.iloc[2])
            )

            st.metric(
                "Jurisdiction",
                str(row.iloc[5])
            )

        st.write(
            "**Distance from first relay:** "
            f"{distance_from_first:.3f} km"
        )

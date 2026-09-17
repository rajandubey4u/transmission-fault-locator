import streamlit as st
import pandas as pd

# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="Transmission Line Fault Locator",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Transmission Line Fault Locator")


# =========================================================
# EXCEL FILE
# =========================================================

FILE = "259-249-250-213-214-233-234.xlsx"


# =========================================================
# LINE CONFIGURATION
#
# The line name gives the direction:
#
# L#259                 MTPS -> RANCHI
# L#249                 RAMGARH -> RANCHI
# L#250                 MTPS -> RAMGARH
# L#213 & L#214         JSR -> BTPS
# L#233 & L234          RAMGARH -> BTPS
# =========================================================

LINES = {
    "L#259 MTPS-RANCHI": {
        "sheet": "L#259 MTPS-RANCHI",
        "first": "MTPS",
        "second": "RANCHI"
    },

    "L#249 RAMGARH-RANCHI": {
        "sheet": "L#249 RAMGARH-RANCHI",
        "first": "RAMGARH",
        "second": "RANCHI"
    },

    "L#250 MTPS-RAMGARH": {
        "sheet": "L#250 MTPS-RAMGARH",
        "first": "MTPS",
        "second": "RAMGARH"
    },

    "L#213 AND L#214 JSR-BTPS": {
        "sheet": "L#213 AND L#214 JSR-BTPS",
        "first": "JSR",
        "second": "BTPS"
    },

    "L#233 AND L234 RAMGARH-BTPS": {
        "sheet": "L#233 AND L234 RAMGARH-BTPS",
        "first": "RAMGARH",
        "second": "BTPS"
    }
}


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    data = {}

    for line_name, config in LINES.items():

        df = pd.read_excel(
            FILE,
            sheet_name=config["sheet"]
        )

        # -------------------------------------------------
        # Convert required columns to numeric
        # -------------------------------------------------

        df["Loc No"] = pd.to_numeric(
            df["Loc No"],
            errors="coerce"
        )

        df["FWD Span"] = pd.to_numeric(
            df["FWD Span"],
            errors="coerce"
        )

        df["SPAN WITH JUMPER ADDED"] = pd.to_numeric(
            df["SPAN WITH JUMPER ADDED"],
            errors="coerce"
        )

        # -------------------------------------------------
        # Calculate cumulative distance ourselves
        #
        # This avoids depending on Excel formulas in Column G
        # -------------------------------------------------

        df["Calculated Cumulative KM"] = (
            df["SPAN WITH JUMPER ADDED"].fillna(0).cumsum()
            / 1000
        )

        data[line_name] = df

    return data


data = load_data()


# =========================================================
# USER INPUT
# =========================================================

line = st.selectbox(
    "Select Transmission Line",
    list(LINES.keys())
)

config = LINES[line]


relay = st.selectbox(
    "Relay Location",
    [
        config["first"],
        config["second"]
    ]
)


fault_distance = st.number_input(
    "Fault Distance Reported by Relay (km)",
    min_value=0.0,
    step=0.001,
    format="%.3f"
)


# =========================================================
# CALCULATE
# =========================================================

if st.button(
    "CALCULATE FAULT LOCATION",
    type="primary",
    use_container_width=True
):

    df = data[line].copy()

    cumulative = df["Calculated Cumulative KM"]

    total_distance = cumulative.iloc[-1]


    # -----------------------------------------------------
    # CHECK RELAY END
    # -----------------------------------------------------

    if relay == config["first"]:

        distance_from_first = fault_distance

    else:

        distance_from_first = (
            total_distance - fault_distance
        )


    # -----------------------------------------------------
    # CHECK DISTANCE
    # -----------------------------------------------------

    if fault_distance > total_distance:

        st.error(
            f"Fault distance is greater than the "
            f"total line length of {total_distance:.3f} km."
        )

    elif distance_from_first < 0:

        st.error(
            "Invalid fault distance."
        )

    else:

        # -------------------------------------------------
        # FIND TOWER
        #
        # The fault belongs to the tower/span whose
        # cumulative distance is immediately before the
        # calculated fault distance.
        # -------------------------------------------------

        valid_rows = df[
            df["Calculated Cumulative KM"]
            <= distance_from_first
        ]

        if len(valid_rows) == 0:

            # Fault before first tower
            row = df.iloc[0]

        else:

            row = valid_rows.iloc[-1]


        # -------------------------------------------------
        # RESULTS
        # -------------------------------------------------

        st.divider()

        st.subheader("Fault Location")


        # Distance information

        st.write(
            f"**Relay Location:** {relay}"
        )

        st.write(
            f"**Fault Distance Reported by Relay:** "
            f"{fault_distance:.3f} km"
        )

        st.write(
            f"**Distance from {config['first']}:** "
            f"{distance_from_first:.3f} km"
        )

        st.write(
            f"**Total Line Length:** "
            f"{total_distance:.3f} km"
        )


        st.divider()


        # -------------------------------------------------
        # TOWER RESULTS
        # -------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Tower Number",
                str(row["Tower Num"])
            )

        with col2:

            st.metric(
                "Tower Type",
                str(row["Type"])
            )

        with col3:

            st.metric(
                "Jurisdiction",
                str(row["Jurisdiction"])
            )


        st.divider()


        # -------------------------------------------------
        # ADDITIONAL INFORMATION
        # -------------------------------------------------

        st.write(
            f"**Location No.:** {row['Loc No']}"
        )

        st.write(
            f"**Cumulative Distance at Tower:** "
            f"{row['Calculated Cumulative KM']:.3f} km"
        )

        st.write(
            f"**Line:** {line}"
        )

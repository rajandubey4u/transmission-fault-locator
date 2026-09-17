import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------------

st.set_page_config(
    page_title="Transmission Line Fault Locator",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Transmission Line Fault Locator")

st.write(
    "Enter the fault distance reported by the relay "
    "to identify the corresponding tower."
)


# ---------------------------------------------------------
# LINE CONFIGURATION
# ---------------------------------------------------------

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

    "L#213 AND L#214 BTPS-JSR": {
        "sheet": "L#213 AND L#214 BTPS-JSR",
        "first": "BTPS",
        "second": "JSR"
    },

    "L#233 AND L234 BTPS-RAMGARH": {
        "sheet": "L#233 AND L234 BTPS-RAMGARH",
        "first": "BTPS",
        "second": "RAMGARH"
    }
}


# ---------------------------------------------------------
# LOAD EXCEL DATA
# ---------------------------------------------------------

FILE = "259-249-250-213-214-233-234.xlsx"


@st.cache_data
def load_data():

    data = {}

    for line_name, config in LINES.items():

        df = pd.read_excel(
            FILE,
            sheet_name=config["sheet"]
        )

        # Make sure cumulative distance is numeric
        df["Cumulative span length ( KM)"] = pd.to_numeric(
            df["Cumulative span length ( KM)"],
            errors="coerce"
        )

        # Remove rows where cumulative distance is unavailable
        df = df.dropna(
            subset=["Cumulative span length ( KM)"]
        )

        data[line_name] = df

    return data


data = load_data()


# ---------------------------------------------------------
# USER INPUT
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# CALCULATE
# ---------------------------------------------------------

if st.button(
    "CALCULATE FAULT LOCATION",
    type="primary",
    use_container_width=True
):

    df = data[line]

    cumulative_column = "Cumulative span length ( KM)"

    # Total line length
    total_distance = df[cumulative_column].max()

    # -----------------------------------------------------
    # CHECK WHETHER RELAY IS AT FIRST OR SECOND END
    # -----------------------------------------------------

    if relay == config["first"]:

        distance_from_first = fault_distance

    else:

        distance_from_first = (
            total_distance - fault_distance
        )


    # -----------------------------------------------------
    # VALIDATE DISTANCE
    # -----------------------------------------------------

    if fault_distance > total_distance:

        st.error(
            f"Entered fault distance ({fault_distance:.3f} km) "
            f"is greater than the total line length "
            f"({total_distance:.3f} km)."
        )

    else:

        # -------------------------------------------------
        # FIND THE TOWER
        # -------------------------------------------------
        #
        # Find the last row whose cumulative distance
        # is less than or equal to the calculated distance.
        #
        # This corresponds to the tower/span containing
        # the fault.
        # -------------------------------------------------

        valid_rows = df[
            df[cumulative_column] <= distance_from_first
        ]

        if len(valid_rows) == 0:

            st.error(
                "The fault distance falls before the first "
                "available tower in the data."
            )

        else:

            row = valid_rows.iloc[-1]


            # -------------------------------------------------
            # RESULT
            # -------------------------------------------------

            st.divider()

            st.subheader("Fault Location")


            # Distance information

            st.write(
                f"**Relay:** {relay}"
            )

            st.write(
                f"**Distance reported by relay:** "
                f"{fault_distance:.3f} km"
            )

            st.write(
                f"**Distance from {config['first']}:** "
                f"{distance_from_first:.3f} km"
            )


            st.divider()


            # Tower information

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Tower Number",
                    str(row["Tower Num"])
                )

                st.metric(
                    "Tower Type",
                    str(row["Type"])
                )

            with col2:

                st.metric(
                    "Jurisdiction",
                    str(row["Jurisdiction"])
                )

                st.metric(
                    "Location No.",
                    str(row["Loc No"])
                )


            # -------------------------------------------------
            # ADDITIONAL INFORMATION
            # -------------------------------------------------

            st.divider()

            st.write(
                f"**Cumulative distance at tower:** "
                f"{row[cumulative_column]:.3f} km"
            )

            st.write(
                f"**Line:** {line}"
            )

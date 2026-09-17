import streamlit as st
import pandas as pd
import re

# =========================================================
# CONFIGURATION-1
# =========================================================

FILE = "259-249-250-213-214-233-234.xlsx"

SHEETS = [
    "L#259 MTPS-RANCHI",
    "L#249 RAMGARH-RANCHI",
    "L#250 MTPS-RAMGARH",
    "L#213 AND L#214 JSR-BTPS",
    "L#233 AND L234 RAMGARH-BTPS"
]


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Line Fault Location Calculator",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

/* Main page */
.block-container {
    width: 100%;
    max-width: 720px;
    margin: auto;
    padding-top: 0.8rem;
    padding-left: 1rem;
    padding-right: 1rem;
    padding-bottom: 1.5rem;
    box-sizing: border-box;
}


/* Main heading */
h1 {
    text-align: center !important;
    font-size: 30px !important;
    font-weight: 800 !important;
    line-height: 1.2 !important;
    margin-top: 0 !important;
    margin-bottom: 4px !important;
}


/* Subtitle */
.subtitle {
    text-align: center;
    font-size: 13px;
    font-weight: 600;
    opacity: 0.65;
    line-height: 1.4;
    margin-bottom: 18px;
}


/* Input labels */
label {
    font-weight: 700 !important;
    font-size: 15px !important;
}


/* Red calculate button */
div.stButton > button {
    width: 100%;
    min-height: 48px;
    border-radius: 9px;
    background-color: #d32f2f;
    color: white;
    border: none;
    font-size: 16px;
    font-weight: 750;
}

div.stButton > button:hover {
    background-color: #b71c1c;
    color: white;
}

div.stButton > button:focus {
    background-color: #c62828;
    color: white;
}


/* Result heading */
.result-heading {
    font-size: 17px;
    font-weight: 800;
    margin-top: 18px;
    margin-bottom: 7px;
}


/* Footer */
.footer {
    text-align: center;
    font-size: 12px;
    font-weight: 600;
    opacity: 0.55;
    margin-top: 25px;
}


/* Mobile */
@media (max-width: 600px) {

    .block-container {
        padding-left: 0.7rem;
        padding-right: 0.7rem;
        padding-top: 0.5rem;
    }

    h1 {
        font-size: 24px !important;
    }

    .subtitle {
        font-size: 11px;
        margin-bottom: 15px;
    }

    label {
        font-size: 14px !important;
    }

}


/* Small phones */
@media (max-width: 380px) {

    h1 {
        font-size: 21px !important;
    }

    .subtitle {
        font-size: 10px;
    }

}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.title("Line Fault Location Calculator")

st.markdown(
    '<div class="subtitle">'
    'Transmission Line Fault Location & Patrol Tower Identification'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# LOAD EXCEL
# =========================================================

@st.cache_data
def load_excel():

    data = {}

    for sheet in SHEETS:

        df = pd.read_excel(
            FILE,
            sheet_name=sheet
        )

        # Clean column names
        df.columns = [
            str(c).strip()
            for c in df.columns
        ]

        # Required columns
        required_columns = [
            "Loc No",
            "Tower Num",
            "Type",
            "Jurisdiction"
        ]

        missing = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing:

            raise ValueError(
                f"{sheet}: Missing columns {missing}"
            )

        # -------------------------------------------------
        # COLUMN G
        # -------------------------------------------------
        # Column G is the required cumulative distance.
        # Column E is completely ignored.
        # -------------------------------------------------

        if len(df.columns) < 7:

            raise ValueError(
                f"{sheet}: Column G not found."
            )

        column_g = df.columns[6]

        df["_DISTANCE_G"] = pd.to_numeric(
            df[column_g],
            errors="coerce"
        )

        data[sheet] = df

    return data


# =========================================================
# LOAD DATA
# =========================================================

try:

    DATA = load_excel()

except Exception as error:

    st.error(
        f"❌ Error reading Excel file:\n\n{error}"
    )

    st.stop()


# =========================================================
# SELECT TRANSMISSION LINE
# =========================================================

line_name = st.selectbox(
    "Select Transmission Line",
    SHEETS
)

df = DATA[line_name].copy()


# =========================================================
# LINE END DEFINITIONS
# =========================================================

if line_name == "L#259 MTPS-RANCHI":

    first_end = "MTPS"
    second_end = "RANCHI"

elif line_name == "L#249 RAMGARH-RANCHI":

    first_end = "RAMGARH"
    second_end = "RANCHI"

elif line_name == "L#250 MTPS-RAMGARH":

    first_end = "MTPS"
    second_end = "RAMGARH"

elif line_name == "L#213 AND L#214 JSR-BTPS":

    first_end = "JSR"
    second_end = "BTPS"

elif line_name == "L#233 AND L234 RAMGARH-BTPS":

    first_end = "RAMGARH"
    second_end = "BTPS"

else:

    first_end = "FIRST END"
    second_end = "SECOND END"


# =========================================================
# RELAY LOCATION
# =========================================================

relay_end = st.selectbox(
    "Relay Location",
    [
        first_end,
        second_end
    ]
)


# =========================================================
# VALID COLUMN G DATA
# =========================================================

valid_distance = df[
    df["_DISTANCE_G"].notna()
].copy()


if valid_distance.empty:

    st.error(
        "❌ No valid distance data found in Column G."
    )

    st.stop()


# =========================================================
# TOTAL LINE LENGTH
# =========================================================

total_distance = float(
    valid_distance["_DISTANCE_G"].max()
)


st.info(
    f"Total Line Length: **{total_distance:.3f} km**"
)


# =========================================================
# FAULT DISTANCE INPUT
# =========================================================

# IMPORTANT:
# No max_value is used here.
# This allows the user to enter a value greater than
# the total line length so that the program can warn them.

fault_distance = st.number_input(
    "Fault Distance from Relay (km)",
    min_value=0.0,
    value=0.0,
    step=0.001,
    format="%.3f"
)


# =========================================================
# CALCULATE BUTTON
# =========================================================

calculate = st.button(
    "⚡ CALCULATE FAULT LOCATION",
    use_container_width=True
)


# =========================================================
# CALCULATION
# =========================================================

if calculate:

    # =====================================================
    # OUT OF RANGE CHECK
    # =====================================================

    if fault_distance > total_distance:

        st.error(
            "⚠️ OUT OF RANGE — PLEASE CHECK DATA"
        )

        st.stop()


    # =====================================================
    # DISTANCE FROM FIRST END
    # =====================================================

    if relay_end == first_end:

        distance_from_first = fault_distance

    else:

        distance_from_first = (
            total_distance - fault_distance
        )


    # =====================================================
    # CHECK CONVERTED DISTANCE
    # =====================================================

    if (
        distance_from_first < 0
        or distance_from_first > total_distance
    ):

        st.error(
            "⚠️ OUT OF RANGE — PLEASE CHECK DATA"
        )

        st.stop()


    # =====================================================
    # FIND TOWER USING COLUMN G
    # =====================================================

    sorted_df = valid_distance.sort_values(
        "_DISTANCE_G"
    ).copy()


    matching_rows = sorted_df[
        sorted_df["_DISTANCE_G"]
        >= distance_from_first
    ]


    if matching_rows.empty:

        st.error(
            "⚠️ OUT OF RANGE — PLEASE CHECK DATA"
        )

        st.stop()


    # First matching row
    row = matching_rows.iloc[0]


    # =====================================================
    # GET VALUES
    # =====================================================

    suspected_tower = str(
        row["Tower Num"]
    ).strip()

    tower_type = str(
        row["Type"]
    ).strip()

    jurisdiction = str(
        row["Jurisdiction"]
    ).strip()

    matched_distance = float(
        row["_DISTANCE_G"]
    )


    # =====================================================
    # PATROL TOWERS
    # =====================================================

    # Extract number from Tower Num
    # Example:
    # T324 -> 324
    # T458 -> 458

    tower_match = re.search(
        r"T\s*[-]?\s*(\d+)",
        suspected_tower,
        re.IGNORECASE
    )


    if tower_match:

        tower_number = int(
            tower_match.group(1)
        )


        # -------------------------------------------------
        # Get actual tower number range from Column B
        # -------------------------------------------------

        all_tower_numbers = []

        for value in df["Tower Num"].dropna():

            match = re.search(
                r"T\s*[-]?\s*(\d+)",
                str(value),
                re.IGNORECASE
            )

            if match:

                all_tower_numbers.append(
                    int(match.group(1))
                )


        if all_tower_numbers:

            minimum_tower = min(
                all_tower_numbers
            )

            maximum_tower = max(
                all_tower_numbers
            )

        else:

            minimum_tower = 1
            maximum_tower = tower_number + 5


        # -------------------------------------------------
        # ±5 towers
        # -------------------------------------------------

        patrol_start = max(
            minimum_tower,
            tower_number - 5
        )

        patrol_end = min(
            maximum_tower,
            tower_number + 5
        )


        patrol_towers = [
            f"T{i}"
            for i in range(
                patrol_start,
                patrol_end + 1
            )
        ]


    else:

        patrol_towers = [
            suspected_tower
        ]


    # =====================================================
    # DISPLAY RESULT
    # =====================================================

    st.success(
        "Fault location identified"
    )


    # =====================================================
    # COMPACT RESULT TABLE
    # =====================================================

    result_table = pd.DataFrame(
        {
            "Parameter": [
                "Suspected Tower No.",
                "Tower Type",
                "Jurisdiction",
                "Tower Cumulative Distance"
            ],

            "Result": [
                suspected_tower,
                tower_type,
                jurisdiction,
                f"{matched_distance:.3f} km"
            ]
        }
    )


    st.dataframe(
        result_table,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # PATROLLING TOWERS
    # =====================================================

    st.markdown(
        '<div class="result-heading">'
        '🚶 Patrolling Towers'
        '</div>',
        unsafe_allow_html=True
    )


    # Patrol range
    st.success(
        f"**{patrol_towers[0]} – {patrol_towers[-1]}**"
    )


    # Individual towers
    st.caption(
        "Towers to patrol:"
    )


    st.write(
        " • ".join(patrol_towers)
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    '<div class="footer">'
    'GOMD VII Line Maintenance Dept'
    '</div>',
    unsafe_allow_html=True
)
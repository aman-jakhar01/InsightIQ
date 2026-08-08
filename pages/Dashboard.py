import streamlit as st
import pandas as pd
import plotly.express as px

from utils.kpis import detect_kpis
from utils.ui import apply_insightiq_style


# ---------------------------------------
# Page Configuration
# ---------------------------------------

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

apply_insightiq_style()


# ---------------------------------------
# InsightIQ Header
# ---------------------------------------

st.markdown(
    """
    <div style="
        padding: 1.5rem 1.8rem;
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 16px;
        margin-bottom: 1.5rem;
    ">

    <h1 style="margin-bottom: 0.3rem;">
        📊 InsightIQ
    </h1>

    <p style="
        font-size: 1.15rem;
        margin-bottom: 0.3rem;
    ">
        Intelligent Business Analytics
    </p>

    <p style="
        opacity: 0.7;
        margin-bottom: 0;
    ">
        Upload → Analyze → Predict → Decide
    </p>

    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Upload a CSV or Excel dataset to begin your analysis."
)


# ---------------------------------------
# Dataset Upload
# ---------------------------------------

st.subheader("📤 Upload Dataset")

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx"],
    help="Upload a structured business dataset for analysis."
)


if uploaded_file is not None:

    try:

        if uploaded_file.name.lower().endswith(".csv"):

            df = pd.read_csv(
                uploaded_file
            )

        else:

            df = pd.read_excel(
                uploaded_file
            )

        # Store current dataset
        st.session_state["data"] = df

        # Clear results that belong to a previous dataset
        for key in [
            "historical_forecast",
            "forecast_data",
            "forecast_info",
            "forecast_date_column",
            "forecast_value_column",
            "forecast_explanation",
            "final_executive_report"
        ]:

            st.session_state.pop(
                key,
                None
            )

        st.success(
            f"✅ {uploaded_file.name} uploaded successfully!"
        )

    except Exception as e:

        st.error(
            f"❌ Unable to read the uploaded file: {e}"
        )

        st.stop()


# ---------------------------------------
# Dataset Check
# ---------------------------------------

if "data" not in st.session_state:

    st.info(
        "👆 Upload a dataset above to unlock the InsightIQ dashboard."
    )

    st.stop()


df = st.session_state["data"]


# ---------------------------------------
# Dataset Preview
# ---------------------------------------

st.divider()

st.subheader("🔎 Dataset Preview")

st.dataframe(
    df.head(10),
    use_container_width=True
)


# ---------------------------------------
# Dataset Overview
# ---------------------------------------

st.divider()

st.subheader("📋 Dataset Overview")


rows = df.shape[0]
columns = df.shape[1]

missing_values = int(
    df.isnull().sum().sum()
)

duplicate_rows = int(
    df.duplicated().sum()
)

numeric_columns = len(
    df.select_dtypes(
        include=["number"]
    ).columns
)

categorical_columns = len(
    df.select_dtypes(
        include=["object", "category"]
    ).columns
)


col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Rows",
        f"{rows:,}"
    )

with col2:

    st.metric(
        "Columns",
        f"{columns:,}"
    )

with col3:

    st.metric(
        "Missing Values",
        f"{missing_values:,}"
    )

with col4:

    st.metric(
        "Duplicate Rows",
        f"{duplicate_rows:,}"
    )


col5, col6 = st.columns(2)

with col5:

    st.metric(
        "Numeric Columns",
        numeric_columns
    )

with col6:

    st.metric(
        "Categorical Columns",
        categorical_columns
    )


# ---------------------------------------
# Smart KPIs
# ---------------------------------------

st.divider()

st.subheader("📌 Smart KPIs")

st.caption(
    "InsightIQ automatically detects useful numeric business metrics "
    "from your dataset."
)

kpis = detect_kpis(
    df
)

if kpis:

    kpi_columns = st.columns(
        min(len(kpis), 4)
    )

    for index, kpi in enumerate(kpis):

        column = kpi.get(
            "column",
            "Metric"
        )

        label = kpi.get(
            "label",
            str(column)
        )

        value = kpi.get(
            "value",
            0
        )

        if isinstance(
            value,
            (int, float)
        ):

            if abs(value) >= 1_000_000:

                display_value = (
                    f"{value / 1_000_000:.2f}M"
                )

            elif abs(value) >= 1_000:

                display_value = (
                    f"{value / 1_000:.2f}K"
                )

            else:

                display_value = (
                    f"{value:,.2f}"
                )

        else:

            display_value = str(
                value
            )

        with kpi_columns[
            index % len(kpi_columns)
        ]:

            st.metric(
                label=label,
                value=display_value
            )

else:

    st.info(
        "No suitable numeric KPI columns were detected."
    )


# ---------------------------------------
# Dataset Information
# ---------------------------------------

st.divider()

st.subheader("📑 Dataset Information")

info_col1, info_col2 = st.columns(
    2
)


with info_col1:

    st.markdown(
        "### Dataset Shape"
    )

    st.write(
        f"Rows: **{df.shape[0]:,}**"
    )

    st.write(
        f"Columns: **{df.shape[1]:,}**"
    )

    st.markdown(
        "### Memory Usage"
    )

    memory = (
        df.memory_usage(
            deep=True
        ).sum()
        / 1024**2
    )

    st.write(
        f"{memory:.2f} MB"
    )


with info_col2:

    st.markdown(
        "### Data Types"
    )

    dtype_df = (
        df.dtypes
        .astype(str)
        .reset_index()
    )

    dtype_df.columns = [
        "Column",
        "Data Type"
    ]

    st.dataframe(
        dtype_df,
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------
# Interactive Visualization
# ---------------------------------------

st.divider()

st.subheader(
    "📊 Interactive Data Visualization"
)

st.caption(
    "Explore distributions and category frequencies interactively."
)


numeric_column_list = (
    df.select_dtypes(
        include="number"
    )
    .columns
    .tolist()
)

categorical_column_list = (
    df.select_dtypes(
        include=["object", "category"]
    )
    .columns
    .tolist()
)


viz_col1, viz_col2 = st.columns(
    2
)


with viz_col1:

    st.markdown(
        "### 📈 Numeric Distribution"
    )

    if numeric_column_list:

        histogram_column = st.selectbox(
            "Select Numeric Column",
            numeric_column_list,
            key="dashboard_histogram_column"
        )

        fig = px.histogram(
            df,
            x=histogram_column,
            title=f"Distribution of {histogram_column}"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No numeric columns available for this visualization."
        )


with viz_col2:

    st.markdown(
        "### 📊 Category Distribution"
    )

    if categorical_column_list:

        category_column = st.selectbox(
            "Select Categorical Column",
            categorical_column_list,
            key="dashboard_category_column"
        )

        category_count = (
            df[category_column]
            .value_counts()
            .head(20)
            .reset_index()
        )

        category_count.columns = [
            category_column,
            "Count"
        ]

        fig = px.bar(
            category_count,
            x=category_column,
            y="Count",
            title=f"{category_column} Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No categorical columns available for this visualization."
        )


# ---------------------------------------
# Quick Dataset Quality Summary
# ---------------------------------------

st.divider()

st.subheader(
    "🛡️ Data Quality Snapshot"
)

quality_col1, quality_col2, quality_col3 = st.columns(
    3
)


missing_percentage = 0

if rows > 0 and columns > 0:

    missing_percentage = (
        missing_values
        / (rows * columns)
    ) * 100


with quality_col1:

    st.metric(
        "Missing Data",
        f"{missing_percentage:.2f}%"
    )


with quality_col2:

    duplicate_percentage = 0

    if rows > 0:

        duplicate_percentage = (
            duplicate_rows
            / rows
        ) * 100

    st.metric(
        "Duplicate Data",
        f"{duplicate_percentage:.2f}%"
    )


with quality_col3:

    completeness = (
        100 - missing_percentage
    )

    st.metric(
        "Data Completeness",
        f"{completeness:.2f}%"
    )


# ---------------------------------------
# Footer
# ---------------------------------------

st.divider()

st.caption(
    "Powered by InsightIQ • Groq • LangChain • Streamlit"
)
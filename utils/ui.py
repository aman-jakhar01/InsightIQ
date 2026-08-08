import streamlit as st


def apply_insightiq_style():
    st.markdown(
        """
        <style>

        /* Main application */

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }


        /* Page titles */

        h1 {
            font-weight: 700;
            letter-spacing: -0.5px;
        }


        /* Section headings */

        h2 {
            margin-top: 1.5rem;
        }


        /* Metric cards */

        [data-testid="stMetric"] {
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 12px;
            padding: 1rem;
            background: rgba(128, 128, 128, 0.05);
        }


        /* Buttons */

        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            min-height: 42px;
        }


        /* Download buttons */

        .stDownloadButton > button {
            border-radius: 10px;
            font-weight: 600;
            min-height: 42px;
        }


        /* Chat input */

        [data-testid="stChatInput"] {
            border-radius: 12px;
        }


        /* Containers */

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px;
        }


        /* Dataframes */

        [data-testid="stDataFrame"] {
            border-radius: 10px;
            overflow: hidden;
        }


        /* Captions */

        .stCaption {
            opacity: 0.75;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
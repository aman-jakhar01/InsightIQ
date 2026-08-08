import streamlit as st
import plotly.graph_objects as go

from utils.forecasting import (
    detect_date_columns,
    get_numeric_columns,
    create_forecast
)

from utils.forecast_explanation import (
    generate_forecast_explanation
)

from utils.ui import apply_insightiq_style


# ---------------------------------------
# Page Configuration
# ---------------------------------------

st.set_page_config(
    page_title="Forecasting",
    page_icon="📈",
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
        📈 InsightIQ Forecasting
    </h1>

    <p style="
        font-size: 1.1rem;
        margin-bottom: 0.3rem;
    ">
        Predict future business performance from historical data.
    </p>

    <p style="
        opacity: 0.7;
        margin-bottom: 0;
    ">
        Forecast → Validate → Explain → Decide
    </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------
# Dataset Check
# ---------------------------------------

if "data" not in st.session_state:

    st.warning(
        "⚠️ Please upload a dataset from the Dashboard first."
    )

    st.stop()


df = st.session_state["data"]


# ---------------------------------------
# Detect Columns
# ---------------------------------------

date_columns = detect_date_columns(df)

numeric_columns = get_numeric_columns(df)


if not date_columns:

    st.warning(
        "⚠️ No suitable date/time column was detected "
        "in this dataset."
    )

    st.info(
        "Forecasting requires a date/time column and "
        "a numeric metric."
    )

    st.stop()


if not numeric_columns:

    st.warning(
        "⚠️ No numeric columns are available for forecasting."
    )

    st.stop()


# ---------------------------------------
# Forecast Configuration
# ---------------------------------------

st.subheader("⚙️ Forecast Configuration")

st.caption(
    "Choose the time column, business metric and forecast horizon."
)

config_col1, config_col2, config_col3 = st.columns(3)


with config_col1:

    date_column = st.selectbox(
        "📅 Date Column",
        date_columns,
        key="forecast_date_selector"
    )


with config_col2:

    value_column = st.selectbox(
        "📊 Metric to Forecast",
        numeric_columns,
        key="forecast_value_selector"
    )


with config_col3:

    periods = st.number_input(
        "🔮 Forecast Periods",
        min_value=1,
        max_value=365,
        value=30,
        key="forecast_periods"
    )


st.markdown(
    """
    <div style="
        padding: 0.8rem 1rem;
        border-radius: 10px;
        border: 1px solid rgba(128,128,128,0.20);
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    ">
        <span style="opacity:0.75;">
        The forecasting engine automatically selects an appropriate
        time-series approach based on the available historical data.
        </span>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------
# Generate Forecast
# ---------------------------------------

if st.button(
    "📈 Generate Forecast",
    use_container_width=True,
    key="generate_forecast"
):

    with st.spinner(
        "🤖 InsightIQ is building your forecast..."
    ):

        try:

            historical, forecast, model_info = create_forecast(
                df,
                date_column,
                value_column,
                int(periods)
            )

            st.session_state[
                "historical_forecast"
            ] = historical

            st.session_state[
                "forecast_data"
            ] = forecast

            st.session_state[
                "forecast_info"
            ] = model_info

            st.session_state[
                "forecast_date_column"
            ] = date_column

            st.session_state[
                "forecast_value_column"
            ] = value_column

            # Remove explanation from previous forecast
            st.session_state.pop(
                "forecast_explanation",
                None
            )

            st.success(
                "✅ Forecast generated successfully!"
            )

        except Exception as e:

            st.error(
                f"❌ Forecasting failed: {e}"
            )


# ---------------------------------------
# Display Forecast
# ---------------------------------------

if (
    "historical_forecast" in st.session_state
    and
    "forecast_data" in st.session_state
):

    historical = st.session_state[
        "historical_forecast"
    ]

    forecast = st.session_state[
        "forecast_data"
    ]

    model_info = st.session_state.get(
        "forecast_info"
    )

    forecast_date_column = st.session_state.get(
        "forecast_date_column",
        date_column
    )

    forecast_value_column = st.session_state.get(
        "forecast_value_column",
        value_column
    )


    # ---------------------------------------
    # Safety Check
    # ---------------------------------------

    required_historical_columns = {
        forecast_date_column,
        forecast_value_column
    }

    required_forecast_columns = {
        forecast_date_column,
        forecast_value_column
    }

    if (
        not required_historical_columns.issubset(
            historical.columns
        )
        or
        not required_forecast_columns.issubset(
            forecast.columns
        )
    ):

        st.warning(
            "⚠️ The saved forecast belongs to a different "
            "dataset or column selection."
        )

        if st.button(
            "🔄 Clear Old Forecast",
            key="clear_old_forecast"
        ):

            for key in [
                "historical_forecast",
                "forecast_data",
                "forecast_info",
                "forecast_date_column",
                "forecast_value_column",
                "forecast_explanation"
            ]:

                st.session_state.pop(
                    key,
                    None
                )

            st.rerun()

        st.stop()


    # ---------------------------------------
    # Forecast Model
    # ---------------------------------------

    st.divider()

    st.subheader("🧠 Forecast Model")

    if model_info:

        info1, info2, info3 = st.columns(3)

        with info1:

            st.metric(
                "Model",
                model_info.get(
                    "model",
                    "Unknown"
                )
            )

        with info2:

            st.metric(
                "Frequency",
                model_info.get(
                    "frequency",
                    "Unknown"
                )
            )

        with info3:

            st.metric(
                "Historical Observations",
                model_info.get(
                    "observations",
                    len(historical)
                )
            )


    # ---------------------------------------
    # Forecast Chart
    # ---------------------------------------

    st.divider()

    st.subheader(
        f"📊 {forecast_value_column} Forecast"
    )

    st.caption(
        "Historical performance compared with the projected future values."
    )


    fig = go.Figure()


    fig.add_trace(
        go.Scatter(
            x=historical[
                forecast_date_column
            ],
            y=historical[
                forecast_value_column
            ],
            mode="lines",
            name="Historical"
        )
    )


    fig.add_trace(
        go.Scatter(
            x=forecast[
                forecast_date_column
            ],
            y=forecast[
                forecast_value_column
            ],
            mode="lines",
            name="Forecast",
            line=dict(
                dash="dash"
            )
        )
    )


    fig.update_layout(
        xaxis_title=forecast_date_column,
        yaxis_title=forecast_value_column,
        hovermode="x unified",
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        )
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # ---------------------------------------
    # Forecast Summary
    # ---------------------------------------

    st.divider()

    st.subheader(
        "📋 Forecast Summary"
    )

    first_prediction = forecast[
        forecast_value_column
    ].iloc[0]

    last_prediction = forecast[
        forecast_value_column
    ].iloc[-1]

    current_value = historical[
        forecast_value_column
    ].iloc[-1]


    summary1, summary2, summary3 = st.columns(3)


    with summary1:

        st.metric(
            "Current Value",
            f"{current_value:,.2f}"
        )


    with summary2:

        st.metric(
            "First Forecast",
            f"{first_prediction:,.2f}"
        )


    with summary3:

        st.metric(
            "Final Forecast",
            f"{last_prediction:,.2f}"
        )


    # ---------------------------------------
    # Forecast Outlook
    # ---------------------------------------

    if model_info:

        st.divider()

        st.subheader(
            "📈 Forecast Outlook"
        )

        change = model_info.get(
            "change_percent",
            0
        )

        if change > 0:

            st.success(
                f"📈 Projected change: **+{change:.2f}%**"
            )

        elif change < 0:

            st.warning(
                f"📉 Projected change: **{change:.2f}%**"
            )

        else:

            st.info(
                "The forecast shows approximately no change."
            )


    # ---------------------------------------
    # Forecast Validation
    # ---------------------------------------

    validation = None

    if model_info:

        validation = model_info.get(
            "validation"
        )


    st.divider()

    st.subheader(
        "🎯 Forecast Validation"
    )

    st.caption(
        "Validation uses a time-based holdout from historical data. "
        "Lower MAE, RMSE and MAPE generally indicate lower forecast error."
    )


    if validation:

        validation1, validation2, validation3 = st.columns(3)


        with validation1:

            st.metric(
                "MAE",
                f"{validation['mae']:,.2f}"
            )


        with validation2:

            st.metric(
                "RMSE",
                f"{validation['rmse']:,.2f}"
            )


        with validation3:

            if validation["mape"] is not None:

                st.metric(
                    "MAPE",
                    f"{validation['mape']:.2f}%"
                )

            else:

                st.metric(
                    "MAPE",
                    "N/A"
                )


        mape = validation["mape"]


        if mape is not None:

            if mape < 10:

                st.success(
                    "🟢 Forecast error is relatively low."
                )

            elif mape < 20:

                st.info(
                    "🟡 Forecast has moderate error."
                )

            else:

                st.warning(
                    "🔴 Forecast error is relatively high. "
                    "Use the forecast with caution."
                )


        st.caption(
            f"Validation observations: {validation['test_size']}"
        )


    else:

        st.info(
            "Not enough historical observations to calculate "
            "validation metrics. At least 10 aggregated observations "
            "are recommended."
        )


    # ---------------------------------------
    # AI Forecast Explanation
    # ---------------------------------------

    st.divider()

    st.subheader(
        "🤖 AI Forecast Explanation"
    )

    st.caption(
        "Turn the statistical forecast into a business-focused explanation."
    )


    if st.button(
        "✨ Explain Forecast with AI",
        use_container_width=True,
        key="explain_forecast"
    ):

        with st.spinner(
            "🤖 Analyzing the forecast..."
        ):

            try:

                explanation = generate_forecast_explanation(
                    metric=forecast_value_column,
                    model_info=model_info,
                    historical_value=current_value,
                    first_forecast=first_prediction,
                    final_forecast=last_prediction
                )

                if explanation:

                    st.session_state[
                        "forecast_explanation"
                    ] = explanation

                else:

                    st.warning(
                        "The AI returned an empty explanation."
                    )

            except Exception as e:

                st.error(
                    f"❌ AI explanation failed: {e}"
                )


    # ---------------------------------------
    # AI Explanation Display
    # ---------------------------------------

    if "forecast_explanation" in st.session_state:

        st.markdown(
            "### 💡 AI Business Interpretation"
        )

        with st.container(
            border=True
        ):

            st.markdown(
                st.session_state[
                    "forecast_explanation"
                ]
            )


    # ---------------------------------------
    # Forecast Data
    # ---------------------------------------

    st.divider()

    st.subheader(
        "🔮 Forecast Data"
    )

    st.caption(
        "Detailed future values generated by the forecasting model."
    )

    st.dataframe(
        forecast,
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------
# Footer
# ---------------------------------------

st.divider()

st.caption(
    "Powered by InsightIQ • Groq • LangChain • Streamlit"
)
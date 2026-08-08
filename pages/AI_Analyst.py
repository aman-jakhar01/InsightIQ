import streamlit as st

from utils.llm import ask_llm
from utils.insights import generate_executive_insights
from utils.ui import apply_insightiq_style


# ---------------------------------------
# Page Configuration
# ---------------------------------------

st.set_page_config(
    page_title="AI Analyst",
    page_icon="🤖",
    layout="wide"
)

apply_insightiq_style()


# ---------------------------------------
# Header
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
        🤖 InsightIQ AI Analyst
    </h1>

    <p style="
        font-size: 1.1rem;
        margin-bottom: 0.3rem;
    ">
        Ask questions. Discover insights. Make better decisions.
    </p>

    <p style="
        opacity: 0.7;
        margin-bottom: 0;
    ">
        Powered by your dataset and AI-powered business analysis.
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
# Dataset Context
# ---------------------------------------

st.subheader("📊 Dataset Context")

context1, context2, context3, context4 = st.columns(4)

with context1:
    st.metric(
        "Rows",
        f"{df.shape[0]:,}"
    )

with context2:
    st.metric(
        "Columns",
        f"{df.shape[1]:,}"
    )

with context3:
    st.metric(
        "Missing Values",
        f"{int(df.isnull().sum().sum()):,}"
    )

with context4:
    st.metric(
        "Duplicate Rows",
        f"{int(df.duplicated().sum()):,}"
    )


st.divider()


# ---------------------------------------
# Chat Controls
# ---------------------------------------

control_col1, control_col2 = st.columns(
    [5, 1]
)

with control_col1:

    st.subheader("💬 Ask InsightIQ")

    st.caption(
        "Ask questions about your uploaded dataset in natural language."
    )

with control_col2:

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True,
        key="clear_chat"
    ):

        st.session_state["messages"] = []

        st.rerun()


# ---------------------------------------
# Chat History
# ---------------------------------------

if "messages" not in st.session_state:

    st.session_state["messages"] = []


for message in st.session_state["messages"]:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ---------------------------------------
# Example Questions
# ---------------------------------------

if not st.session_state["messages"]:

    st.markdown(
        "### 💡 Try asking"
    )

    example1, example2, example3 = st.columns(3)

    with example1:

        st.info(
            "What are the main insights from this dataset?"
        )

    with example2:

        st.info(
            "Which columns have missing values?"
        )

    with example3:

        st.info(
            "What trends should I pay attention to?"
        )


# ---------------------------------------
# User Input
# ---------------------------------------

question = st.chat_input(
    "💬 Ask InsightIQ anything about your dataset..."
)


# ---------------------------------------
# Process Question
# ---------------------------------------

if question:

    st.session_state["messages"].append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(
            question
        )


    # -----------------------------------
    # Dataset Summary
    # -----------------------------------

    dataset_summary = f"""
Dataset Shape:
{df.shape}

Columns:
{list(df.columns)}

Data Types:
{df.dtypes.to_string()}

Missing Values:
{df.isnull().sum().to_string()}

Duplicate Rows:
{int(df.duplicated().sum())}

Summary Statistics:
{df.describe(include="all").fillna("").to_string()}

First Five Rows:
{df.head().to_string()}
"""


    prompt = f"""
You are an expert Business Data Analyst.

You have been given the following dataset information:

{dataset_summary}

User Question:
{question}

Instructions:

- Answer only using the dataset information provided.
- Do not invent facts or numbers.
- Be professional and concise.
- Use bullet points when helpful.
- Explain insights clearly.
- If the answer cannot be determined from the dataset,
  say so honestly.
"""


    with st.chat_message("assistant"):

        with st.spinner(
            "🤖 InsightIQ is analyzing your dataset..."
        ):

            try:

                answer = ask_llm(
                    prompt
                )

                st.markdown(
                    "### 📊 Analysis"
                )

                st.markdown(
                    answer
                )

                st.session_state["messages"].append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

            except Exception as e:

                error_message = (
                    f"❌ Error: {e}"
                )

                st.error(
                    error_message
                )

                st.session_state["messages"].append(
                    {
                        "role": "assistant",
                        "content": error_message
                    }
                )


# ---------------------------------------
# AI Executive Insights
# ---------------------------------------

st.divider()

st.subheader(
    "✨ AI Executive Insights"
)

st.caption(
    "Generate a structured executive-level analysis "
    "of the uploaded dataset."
)


if st.button(
    "✨ Generate Executive Insights",
    use_container_width=True,
    key="generate_executive_insights"
):

    with st.spinner(
        "🤖 Generating executive insights..."
    ):

        try:

            report = generate_executive_insights(
                df
            )

            if report:

                st.session_state[
                    "executive_report"
                ] = report

            else:

                st.warning(
                    "The AI returned an empty response."
                )

        except Exception as e:

            st.error(
                f"❌ Unable to generate executive insights: {e}"
            )


# ---------------------------------------
# Executive Report
# ---------------------------------------

if "executive_report" in st.session_state:

    report = st.session_state[
        "executive_report"
    ]

    st.markdown(
        "### 📋 Executive Business Report"
    )

    sections = [
        "📈 Executive Summary",
        "📊 Key Insights",
        "⚠️ Data Quality Issues",
        "📉 Trends",
        "💡 Business Recommendations",
        "🚨 Risks",
        "🎯 Next Steps",
    ]


    for heading in sections:

        marker_h1 = f"# {heading}"
        marker_h2 = f"## {heading}"

        if marker_h1 in report:

            marker = marker_h1

        elif marker_h2 in report:

            marker = marker_h2

        else:

            continue


        content = report.split(
            marker,
            1
        )[1]


        lines = content.splitlines()

        section_lines = []


        for line in lines:

            if (
                line.startswith("# ")
                or
                line.startswith("## ")
            ):

                break

            section_lines.append(
                line
            )


        content = "\n".join(
            section_lines
        ).strip()


        with st.container(
            border=True
        ):

            st.markdown(
                f"### {heading}"
            )

            if content:

                st.markdown(
                    content
                )

            else:

                st.info(
                    "No information was returned for this section."
                )


# ---------------------------------------
# Footer
# ---------------------------------------

st.divider()

st.caption(
    "Powered by InsightIQ • Groq • LangChain • Streamlit"
)
from utils.llm import ask_llm


def generate_executive_insights(df):
    """Generate structured business insights from a pandas DataFrame."""

    # Build compact, useful context for the LLM.
    numeric_summary = df.describe().round(2).to_string()

    missing = (
        df.isnull()
        .sum()
        .sort_values(ascending=False)
        .to_string()
    )

    dataset_summary = f"""
Dataset Shape:
{df.shape}

Columns:
{list(df.columns)}

Data Types:
{df.dtypes.to_string()}

Missing Values by Column:
{missing}

Total Missing Values:
{int(df.isnull().sum().sum())}

Duplicate Rows:
{int(df.duplicated().sum())}

Numeric Summary:
{numeric_summary}

First 10 Rows:
{df.head(10).to_string()}
"""

    prompt = f"""
You are a senior business analyst reviewing a business dataset.

Analyze ONLY the information provided below. Do not invent facts,
numbers, trends, causes, or business outcomes that cannot be supported
by the dataset context.

DATASET CONTEXT
---------------
{dataset_summary}

Return a concise executive-style analysis using exactly these sections:

## 📈 Executive Summary
Give a short overview of the dataset and the most important findings.

## 📊 Key Insights
Give 3-5 important, evidence-based observations.
Include numbers when they are available.

## ⚠️ Data Quality Issues
Identify missing values, duplicates, unusual data-quality concerns,
or limitations visible from the supplied information.
If none are evident, say so.

## 📉 Trends
Describe meaningful patterns or distributions that can actually be
supported by the supplied statistics and sample data.
Do not claim time trends unless a time-related column is available.

## 💡 Business Recommendations
Give practical recommendations based on the observed evidence.
Clearly distinguish recommendations from confirmed facts.

## 🚨 Risks
Identify potential business or analytical risks.
Do not present speculation as fact.

## 🎯 Next Steps
Give 3-5 concrete actions an analyst or business team should take next.

IMPORTANT:
- Be concise and professional.
- Do not invent information.
- Do not claim causation unless the data supports it.
- If the available context is insufficient for a conclusion, explicitly say so.
"""

    return ask_llm(prompt)
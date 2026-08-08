from io import BytesIO

import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _safe(value, default="N/A"):
    if value is None:
        return default
    return str(value)


def _format_value(value):
    if isinstance(value, (int, float)):
        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        if abs(value) >= 1_000:
            return f"{value / 1_000:.2f}K"
        return f"{value:,.2f}"
    return _safe(value)


def _build_forecast_chart(historical, forecast, date_column, value_column):
    """
    Create a PNG forecast chart in memory for embedding in the PDF.
    """

    if historical is None or forecast is None:
        return None

    if date_column not in historical.columns:
        return None

    if value_column not in historical.columns:
        return None

    if date_column not in forecast.columns:
        return None

    if value_column not in forecast.columns:
        return None

    buffer = BytesIO()

    plt.figure(figsize=(10, 4.8))

    plt.plot(
        historical[date_column],
        historical[value_column],
        label="Historical",
    )

    plt.plot(
        forecast[date_column],
        forecast[value_column],
        linestyle="--",
        label="Forecast",
    )

    plt.title(f"{value_column} Forecast")
    plt.xlabel(date_column)
    plt.ylabel(value_column)
    plt.legend()
    plt.grid(alpha=0.2)
    plt.xticks(rotation=30)
    plt.tight_layout()

    plt.savefig(
        buffer,
        format="png",
        dpi=160,
        bbox_inches="tight",
    )

    plt.close()

    buffer.seek(0)

    return buffer


def create_executive_pdf(
    df,
    kpis=None,
    executive_insights=None,
    forecast_info=None,
    forecast_explanation=None,
    historical=None,
    forecast=None,
    forecast_date_column=None,
    forecast_value_column=None,
):
    """
    Create a professional InsightIQ Executive Report PDF.

    Returns PDF bytes.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="InsightIQ Executive Business Report",
        author="InsightIQ",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "InsightIQTitle",
        parent=styles["Title"],
        fontSize=25,
        leading=30,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "InsightIQSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        alignment=TA_CENTER,
        spaceAfter=20,
    )

    section_style = ParagraphStyle(
        "InsightIQSection",
        parent=styles["Heading2"],
        fontSize=16,
        leading=20,
        spaceBefore=12,
        spaceAfter=9,
    )

    body_style = ParagraphStyle(
        "InsightIQBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=6,
    )

    small_style = ParagraphStyle(
        "InsightIQSmall",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
    )

    story = []

    # ---------------------------------------
    # Cover / Header
    # ---------------------------------------

    story.append(
        Spacer(1, 18 * mm)
    )

    story.append(
        Paragraph(
            "📊 InsightIQ",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Executive Business Report",
            subtitle_style,
        )
    )

    story.append(
        Paragraph(
            "Intelligent Analytics • Forecasting • AI Insights",
            subtitle_style,
        )
    )

    story.append(
        Spacer(1, 8 * mm)
    )

    # ---------------------------------------
    # Dataset Overview
    # ---------------------------------------

    story.append(
        Paragraph(
            "📋 Dataset Overview",
            section_style,
        )
    )

    rows = len(df)
    columns = len(df.columns)
    missing = int(df.isnull().sum().sum())
    duplicates = int(df.duplicated().sum())
    numeric = len(df.select_dtypes(include="number").columns)
    categorical = len(
        df.select_dtypes(
            include=["object", "category"]
        ).columns
    )

    overview_data = [
        [
            "Rows",
            "Columns",
            "Missing Values",
            "Duplicate Rows",
        ],
        [
            f"{rows:,}",
            f"{columns:,}",
            f"{missing:,}",
            f"{duplicates:,}",
        ],
        [
            "Numeric Columns",
            "Categorical Columns",
            "Data Completeness",
            "Dataset Size",
        ],
        [
            f"{numeric:,}",
            f"{categorical:,}",
            f"{(100 - (missing / max(rows * columns, 1) * 100)):.2f}%",
            f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB",
        ],
    ]

    overview_table = Table(
        overview_data,
        colWidths=[
            43 * mm,
            43 * mm,
            43 * mm,
            43 * mm,
        ],
    )

    overview_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("BACKGROUND", (0, 2), (-1, 2), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(overview_table)

    # ---------------------------------------
    # Smart KPIs
    # ---------------------------------------

    if kpis:

        story.append(
            Paragraph(
                "📌 Smart KPIs",
                section_style,
            )
        )

        kpi_data = [["Metric", "Value"]]

        for kpi in kpis:

            label = kpi.get(
                "label",
                kpi.get("column", "Metric"),
            )

            value = kpi.get(
                "value",
                "N/A",
            )

            kpi_data.append(
                [
                    _safe(label),
                    _format_value(value),
                ]
            )

        kpi_table = Table(
            kpi_data,
            colWidths=[
                95 * mm,
                75 * mm,
            ],
        )

        kpi_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(kpi_table)

    # ---------------------------------------
    # Executive Insights
    # ---------------------------------------

    if executive_insights:

        story.append(
            Paragraph(
                "✨ Executive Insights",
                section_style,
            )
        )

        for paragraph in str(
            executive_insights
        ).split("\n"):

            paragraph = paragraph.strip()

            if not paragraph:
                continue

            clean = (
                paragraph
                .replace("#", "")
                .replace("**", "")
            )

            story.append(
                Paragraph(
                    clean,
                    body_style,
                )
            )

    # ---------------------------------------
    # Forecast
    # ---------------------------------------

    if forecast_info:

        story.append(
            PageBreak()
        )

        story.append(
            Paragraph(
                "📈 Forecast Analysis",
                section_style,
            )
        )

        forecast_rows = [
            ["Forecast Attribute", "Value"],
            [
                "Model",
                _safe(
                    forecast_info.get(
                        "model"
                    )
                ),
            ],
            [
                "Frequency",
                _safe(
                    forecast_info.get(
                        "frequency"
                    )
                ),
            ],
            [
                "Historical Observations",
                _safe(
                    forecast_info.get(
                        "observations"
                    )
                ),
            ],
            [
                "Forecast Periods",
                _safe(
                    forecast_info.get(
                        "forecast_periods"
                    )
                ),
            ],
            [
                "Projected Change",
                f"{forecast_info.get('change_percent', 0):.2f}%",
            ],
        ]

        forecast_table = Table(
            forecast_rows,
            colWidths=[
                85 * mm,
                85 * mm,
            ],
        )

        forecast_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(forecast_table)
        story.append(Spacer(1, 8))

        chart_buffer = _build_forecast_chart(
            historical,
            forecast,
            forecast_date_column,
            forecast_value_column,
        )

        if chart_buffer:

            story.append(
                Paragraph(
                    "Historical vs Forecast",
                    ParagraphStyle(
                        "ChartHeading",
                        parent=body_style,
                        fontName="Helvetica-Bold",
                        fontSize=11,
                    ),
                )
            )

            story.append(
                Image(
                    chart_buffer,
                    width=175 * mm,
                    height=84 * mm,
                )
            )

        # -----------------------------------
        # Validation
        # -----------------------------------

        validation = forecast_info.get(
            "validation"
        )

        if validation:

            story.append(
                Paragraph(
                    "🎯 Forecast Validation",
                    section_style,
                )
            )

            mape = validation.get(
                "mape"
            )

            validation_rows = [
                ["Metric", "Result"],
                [
                    "MAE",
                    f"{validation.get('mae', 0):,.2f}",
                ],
                [
                    "RMSE",
                    f"{validation.get('rmse', 0):,.2f}",
                ],
                [
                    "MAPE",
                    (
                        f"{mape:.2f}%"
                        if mape is not None
                        else "N/A"
                    ),
                ],
                [
                    "Validation Observations",
                    str(
                        validation.get(
                            "test_size",
                            "N/A"
                        )
                    ),
                ],
            ]

            validation_table = Table(
                validation_rows,
                colWidths=[
                    85 * mm,
                    85 * mm,
                ],
            )

            validation_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )

            story.append(validation_table)

    # ---------------------------------------
    # AI Forecast Explanation
    # ---------------------------------------

    if forecast_explanation:

        story.append(
            Paragraph(
                "🤖 AI Forecast Explanation",
                section_style,
            )
        )

        for paragraph in str(
            forecast_explanation
        ).split("\n"):

            paragraph = paragraph.strip()

            if not paragraph:
                continue

            clean = (
                paragraph
                .replace("#", "")
                .replace("**", "")
            )

            story.append(
                Paragraph(
                    clean,
                    body_style,
                )
            )

    # ---------------------------------------
    # Footer
    # ---------------------------------------

    story.append(
        Spacer(1, 12 * mm)
    )

    story.append(
        Paragraph(
            "Generated by InsightIQ • Groq • LangChain • Streamlit",
            small_style,
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()
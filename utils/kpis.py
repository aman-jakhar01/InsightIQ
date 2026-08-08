import pandas as pd


def detect_kpis(df, max_kpis=4):
    """
    Automatically detect useful numeric KPIs from a dataset.

    Returns a list of dictionaries containing:
    column, value, and label.
    """

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    if not numeric_columns:
        return []

    kpis = []

    priority_keywords = [
        "revenue",
        "sales",
        "profit",
        "income",
        "amount",
        "price",
        "value",
        "cost",
        "orders",
        "customers",
        "quantity",
        "units",
        "salary",
        "score",
        "rating"
    ]

    # Prefer columns whose names look like business metrics.
    prioritized = []

    for column in numeric_columns:

        column_name = str(column).lower()

        score = 0

        for keyword in priority_keywords:

            if keyword in column_name:
                score += 1

        prioritized.append(
            (score, column)
        )

    prioritized.sort(
        key=lambda item: item[0],
        reverse=True
    )

    selected_columns = [
        column
        for _, column in prioritized[:max_kpis]
    ]

    for column in selected_columns:

        series = df[column].dropna()

        if series.empty:
            continue

        total = series.sum()

        kpis.append(
            {
                "column": column,
                "label": str(column),
                "value": total
            }
        )

    return kpis
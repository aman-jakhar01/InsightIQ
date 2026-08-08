import numpy as np
import pandas as pd

from statsmodels.tsa.holtwinters import ExponentialSmoothing


FORECASTING_VERSION = "3.0"


def detect_date_columns(df):
    """
    Detect columns that can reasonably be interpreted as dates.
    """

    date_columns = []

    for column in df.columns:

        if pd.api.types.is_datetime64_any_dtype(df[column]):
            date_columns.append(column)
            continue

        if df[column].dtype == "object":

            converted = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            valid_ratio = converted.notna().mean()

            if valid_ratio >= 0.8:
                date_columns.append(column)

    return date_columns


def get_numeric_columns(df):
    """
    Return numeric columns suitable for forecasting.
    """

    return df.select_dtypes(
        include=np.number
    ).columns.tolist()


def prepare_time_series(
    df,
    date_column,
    value_column
):
    """
    Clean and aggregate the selected time series.
    """

    if date_column not in df.columns:
        raise ValueError(
            f"Date column '{date_column}' was not found in the dataset."
        )

    if value_column not in df.columns:
        raise ValueError(
            f"Numeric column '{value_column}' was not found in the dataset."
        )

    data = df[
        [date_column, value_column]
    ].copy()

    data[date_column] = pd.to_datetime(
        data[date_column],
        errors="coerce"
    )

    data[value_column] = pd.to_numeric(
        data[value_column],
        errors="coerce"
    )

    data = data.dropna()

    if data.empty:
        raise ValueError(
            "No valid date/numeric observations were found."
        )

    data = (
        data
        .groupby(date_column)[value_column]
        .sum()
        .reset_index()
    )

    data = data.sort_values(
        date_column
    )

    return data


def detect_frequency(data, date_column):
    """
    Detect the approximate frequency of the time series.
    """

    dates = data[date_column].sort_values()

    if len(dates) < 3:
        return "D"

    differences = dates.diff().dropna()

    median_days = (
        differences.dt.total_seconds().median()
        / 86400
    )

    if median_days <= 1.5:
        return "D"

    if median_days <= 8:
        return "W"

    if median_days <= 31:
        return "MS"

    if median_days <= 92:
        return "QS"

    return "YS"


def _fit_and_forecast(
    series,
    frequency,
    periods
):
    """
    Fit Holt/Holt-Winters and return predictions + model name.
    """

    seasonal_periods = None

    if frequency == "D" and len(series) >= 14:
        seasonal_periods = 7

    elif frequency == "W" and len(series) >= 12:
        seasonal_periods = 4

    elif frequency == "MS" and len(series) >= 24:
        seasonal_periods = 12

    try:

        if seasonal_periods:

            model = ExponentialSmoothing(
                series,
                trend="add",
                seasonal="add",
                seasonal_periods=seasonal_periods
            )

        else:

            model = ExponentialSmoothing(
                series,
                trend="add",
                seasonal=None
            )

        fitted_model = model.fit(
            optimized=True
        )

        predictions = fitted_model.forecast(
            periods
        )

        model_name = (
            "Holt-Winters Exponential Smoothing"
            if seasonal_periods
            else "Holt Exponential Smoothing"
        )

        return np.asarray(predictions), model_name

    except Exception:

        # Reliable simple fallback
        if len(series) < 2:
            raise ValueError(
                "Not enough observations to build a forecast."
            )

        x = np.arange(len(series))

        coefficients = np.polyfit(
            x,
            series.values,
            1
        )

        trend_model = np.poly1d(
            coefficients
        )

        future_x = np.arange(
            len(series),
            len(series) + periods
        )

        predictions = trend_model(
            future_x
        )

        return (
            np.asarray(predictions),
            "Linear Trend Fallback"
        )


def evaluate_forecast(
    data,
    date_column,
    value_column
):
    """
    Evaluate the forecasting approach using a time-based holdout.

    The final 20% of historical observations are held out.
    The model is trained on the earlier observations and compared
    with the held-out actual values.

    Returns:
        Dictionary containing MAE, RMSE, MAPE and test size,
        or None when there are not enough observations.
    """

    series = data[value_column].astype(float)

    if len(series) < 10:
        return None

    test_size = max(
        2,
        int(len(series) * 0.20)
    )

    if len(series) - test_size < 5:
        return None

    train = series.iloc[:-test_size]
    test = series.iloc[-test_size:]

    train_data = data.iloc[:-test_size].copy()

    frequency = detect_frequency(
        train_data,
        date_column
    )

    try:

        predictions, _ = _fit_and_forecast(
            train,
            frequency,
            test_size
        )

    except Exception:
        return None

    actual = test.to_numpy(dtype=float)
    predicted = np.asarray(
        predictions,
        dtype=float
    )

    if len(predicted) != len(actual):
        return None

    errors = actual - predicted

    mae = np.mean(
        np.abs(errors)
    )

    rmse = np.sqrt(
        np.mean(errors ** 2)
    )

    non_zero_actual = actual != 0

    if np.any(non_zero_actual):

        mape = np.mean(
            np.abs(
                errors[non_zero_actual]
                / actual[non_zero_actual]
            )
        ) * 100

    else:

        mape = None

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "mape": (
            float(mape)
            if mape is not None
            else None
        ),
        "test_size": int(test_size)
    }


def create_forecast(
    df,
    date_column,
    value_column,
    periods=30
):
    """
    Generate a forecast using Holt/Holt-Winters
    Exponential Smoothing.

    Returns:
        historical DataFrame
        forecast DataFrame
        model information dictionary
    """

    data = prepare_time_series(
        df,
        date_column,
        value_column
    )

    if len(data) < 5:

        raise ValueError(
            "At least 5 valid observations are required "
            "for forecasting."
        )

    frequency = detect_frequency(
        data,
        date_column
    )

    series = data[
        value_column
    ].astype(float)

    predictions, model_name = _fit_and_forecast(
        series,
        frequency,
        int(periods)
    )

    # ---------------------------------------
    # Create future dates
    # ---------------------------------------

    last_date = data[
        date_column
    ].iloc[-1]

    future_dates = pd.date_range(
        start=last_date,
        periods=int(periods) + 1,
        freq=frequency
    )[1:]

    forecast = pd.DataFrame(
        {
            date_column: future_dates,
            value_column: predictions
        }
    )

    # ---------------------------------------
    # Forecast information
    # ---------------------------------------

    current_value = float(
        series.iloc[-1]
    )

    final_value = float(
        forecast[value_column].iloc[-1]
    )

    if current_value != 0:

        change_percent = (
            (final_value - current_value)
            / abs(current_value)
        ) * 100

    else:

        change_percent = 0.0

    validation = evaluate_forecast(
        data,
        date_column,
        value_column
    )

    model_info = {
        "model": model_name,
        "frequency": frequency,
        "observations": len(series),
        "forecast_periods": int(periods),
        "current_value": current_value,
        "final_forecast": final_value,
        "change_percent": float(change_percent),
        "validation": validation
    }

    return (
        data,
        forecast,
        model_info
    )
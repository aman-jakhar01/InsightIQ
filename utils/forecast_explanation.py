from utils.llm import ask_llm


def generate_forecast_explanation(
    metric,
    model_info,
    historical_value,
    first_forecast,
    final_forecast
):
    """
    Generate an AI-powered business explanation
    using only calculated forecast information.
    """

    validation = model_info.get(
        "validation"
    )

    if validation:

        mae = validation.get(
            "mae"
        )

        rmse = validation.get(
            "rmse"
        )

        mape = validation.get(
            "mape"
        )

    else:

        mae = None
        rmse = None
        mape = None

    prompt = f"""
You are a senior business data analyst.

Explain the following forecast for a business user.

IMPORTANT:
- Use ONLY the information provided below.
- Do not invent statistics, causes, trends, or business facts.
- Do not create numbers that are not provided.
- Clearly distinguish calculated results from interpretation.
- Keep the explanation practical and concise.

FORECAST INFORMATION

Metric:
{metric}

Forecast Model:
{model_info.get("model", "Unknown")}

Detected Frequency:
{model_info.get("frequency", "Unknown")}

Historical Observations:
{model_info.get("observations", "Unknown")}

Forecast Periods:
{model_info.get("forecast_periods", "Unknown")}

Current Historical Value:
{historical_value}

First Forecast Value:
{first_forecast}

Final Forecast Value:
{final_forecast}

Projected Change:
{model_info.get("change_percent", 0):.2f}%

Validation MAE:
{mae if mae is not None else "Not available"}

Validation RMSE:
{rmse if rmse is not None else "Not available"}

Validation MAPE:
{f"{mape:.2f}%" if mape is not None else "Not available"}


Return the explanation using exactly these sections:

## 📈 Forecast Summary

Explain what the forecast indicates.

## 🔍 Forecast Interpretation

Explain the direction and magnitude of the projected change.

## 🎯 Forecast Reliability

Discuss the validation results if available.
Do not call the forecast accurate unless the supplied
validation metrics support that statement.

## 💡 Business Implications

Explain what a business user should consider based
only on the supplied forecast.

## ⚠️ Important Considerations

Mention limitations such as limited observations,
forecast uncertainty, or high validation error when
supported by the provided information.
"""

    return ask_llm(prompt)
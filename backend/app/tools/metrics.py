from langchain.tools import tool


def calculate_error_rate(total: int, errors: int) -> float:
    if total <= 0:
        return 0.0
    safe_errors = max(0, min(errors, total))
    return safe_errors / total


def classify_incident_impact(error_rate: float, duration_minutes: float | None) -> str:
    duration = duration_minutes or 0.0
    if error_rate >= 0.2 or duration >= 60:
        return "high"
    if error_rate >= 0.05 or duration >= 20:
        return "medium"
    return "low"


@tool
def compute_error_rate(total: int, errors: int) -> float:
    """Calculate error rate from total requests and error count."""
    return calculate_error_rate(total, errors)

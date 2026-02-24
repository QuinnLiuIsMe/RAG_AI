from langchain.tools import tool

@tool
def compute_error_rate(total: int, errors: int) -> float:
    """Calculate error rate from total requests and error count."""
    if total == 0:
        return 0.0
    return errors / total

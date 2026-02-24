from langchain.tools import tool

@tool
def calculator(expression: str) -> str:
    """Use this tool to evaluate mathematical expressions."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {str(e)}"

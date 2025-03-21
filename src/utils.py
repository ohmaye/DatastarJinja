"""
Utility functions for the application
"""

from fastapi import Request


def is_datastar(req):
    """
    Check if the request is from DataStar.

    Args:
        req: The request object

    Returns:
        True if the request is from DataStar, False otherwise
    """
    return req.headers.get("Datastar-Request") == "true"


def render_html(request: Request, template: str, context: dict) -> str:
    """
    Render a template with the given context.
    """
    if is_datastar(request):
        context["standalone"] = True
    else:
        context["standalone"] = False

    return None


# Add custom Jinja2 filters
def format_datetime(value):
    if isinstance(value, str):
        try:
            dt = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value
        return dt.strftime("%Y-%m-%d %H:%M")
    elif isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return value

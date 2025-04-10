"""
Utility functions for the application
"""

from fastapi import Request
from fastapi.responses import HTMLResponse
import datetime
from typing import Dict, Any, List, Optional, TypeVar, Union, Type
from pydantic import BaseModel

# Type variable for Pydantic models
T = TypeVar("T", bound=BaseModel)


def is_datastar(req):
    """
    Check if the request is from DataStar.

    Args:
        req: The request object

    Returns:
        True if the request is from DataStar, False otherwise
    """
    return req.headers.get("Datastar-Request") == "true"


def prepare_table_context(
    request: Request,
    table_config,
    items: List[Union[Dict[str, Any], BaseModel]] = None,
    filters: Dict[str, str] = None,
    sort_by: Optional[str] = None,
    sort_asc: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Prepares a unified context for table templates.

    Args:
        request: The request object
        table_config: The TableConfig Pydantic model instance
        items: List of items to display in the table, can be dicts or Pydantic models
        filters: Any active filters
        sort_by: Field to sort by
        sort_asc: Sort direction (True for ascending)

    Returns:
        A dictionary with the complete context for table rendering
    """
    # Use defaults from table_config if parameters aren't provided
    sort_by = sort_by or table_config.default_sort_by
    sort_asc = sort_asc if sort_asc is not None else table_config.default_sort_asc
    items = items or []
    filters = filters or {}

    # Convert any Pydantic models in the items list to dictionaries
    processed_items = []
    for item in items:
        if isinstance(item, BaseModel):
            processed_items.append(item.dict())
        else:
            processed_items.append(item)

    # Build the context with table_config as the central source of truth
    return {
        "request": request,
        "standalone": is_datastar(request),
        "entity_name": table_config.entity_name,
        "entity_title": table_config.entity_title,
        "entity_title_singular": table_config.entity_title_singular,
        "table_config": table_config.dict(),
        "table_template": table_config.table_template,
        "items": processed_items,  # Generic name for table items
        f"{table_config.entity_name}s": processed_items,  # Also include with specific name (e.g. "courses")
        "filters": filters,
        "sort_by": sort_by,
        "sort_asc": sort_asc,
        "include_table": True,
    }


def pydantic_to_context(model_instance: Optional[BaseModel]) -> Dict[str, Any]:
    """
    Convert a Pydantic model to a dictionary for use in a template context.
    Returns None if model_instance is None.

    Args:
        model_instance: The Pydantic model instance to convert

    Returns:
        Dictionary representation of the model, or None
    """
    if model_instance is None:
        return None
    return model_instance.dict()


def response_adapter(
    request: Request,
    template_name: str,
    context: dict = None,
    templates=None,
    url=None,
    status_code: int = 200,
):
    """
    Returns either a full HTML response or a Datastar fragment based on the request.
    """
    # We can't import templates directly due to circular imports
    if templates is None:
        from init import templates

    # Avoid circular imports for DatastarFastAPIResponse
    from datastar_py.responses import DatastarFastAPIResponse

    if context is None:
        context = {}

    # Always include the request in the context
    context["request"] = request

    # If this is a Datastar request, return a fragment
    if is_datastar(request):
        # Set standalone to True for fragment rendering
        context["standalone"] = True

        # Pre-render the template to avoid doing it inside the generator
        html_content = templates.get_template(template_name).render(context)

        # Create an optimized async generator function
        async def fragment_generator(sse):
            # Use the provided URL or None if not specified
            if url:
                # Create a wrapper div with the data-replace-url attribute if URL is provided
                # Send the HTML with URL replacement as a single fragment
                yield sse.merge_fragments(
                    [f"""<div id="content" data-replace-url="'{url}'">""", html_content, "</div>"]
                )
            else:
                # Just yield the content without URL replacement
                yield sse.merge_fragments([html_content])

        return DatastarFastAPIResponse(fragment_generator)
    else:
        # Otherwise return a full page
        context["standalone"] = False
        print("RENDERING FULL PAGE")
        return templates.TemplateResponse(
            name=template_name, context=context, status_code=status_code
        )


def render_html(request: Request, template: str, context: dict = None) -> str:
    """
    Render a template with the given context.
    """
    if context is None:
        context = {}

    if is_datastar(request):
        context["standalone"] = True
    else:
        context["standalone"] = False

    return template

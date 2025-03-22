from typing import Dict, List, Optional, Literal, Any, Callable, Union
from pydantic import BaseModel, Field
from enum import Enum
import json


class ColumnRenderer(BaseModel):
    """Define how a column should be rendered"""

    type: Literal["text", "boolean", "date", "enum", "custom"] = "text"
    template: Optional[str] = None  # For custom renderer, reference to Jinja template
    formatter: Optional[str] = None  # Name of Python formatter function


class ColumnSorter(BaseModel):
    """Define how a column can be sorted"""

    enabled: bool = True
    default: bool = False
    direction: Literal["asc", "desc"] = "asc"
    custom_function: Optional[str] = None  # Name of custom sort function


class TableColumn(BaseModel):
    """Definition of a table column"""

    key: str
    label: str
    sortable: bool = True
    filterable: bool = True
    visible: bool = True
    type: str = "text"  # text, boolean, date, select, etc.
    width: Optional[str] = None  # CSS width value
    renderer: Optional[ColumnRenderer] = None
    sorter: Optional[ColumnSorter] = None
    options: Optional[List[Dict[str, str]]] = None  # For select/enum types

    def dict(self, *args, **kwargs):
        """Custom dict method to make column compatible with existing templates"""
        result = super().dict(*args, **kwargs)
        # Remove renderer reference if not specified
        if not result.get("renderer"):
            result.pop("renderer", None)
        return result


class TableConfig(BaseModel):
    """Full table configuration"""

    entity_name: str
    entity_title: Optional[str] = None  # e.g. "Courses"
    entity_title_singular: Optional[str] = None  # e.g. "Course"
    columns: List[TableColumn]
    default_sort_by: Optional[str] = None
    default_sort_asc: bool = True
    enable_pagination: bool = True
    items_per_page: int = 10
    searchable: bool = True
    table_template: Optional[str] = None  # Path to the table template
    action_buttons: Dict[str, bool] = Field(
        default_factory=lambda: {
            "create": True,
            "edit": True,
            "delete": True,
        }
    )

    def __init__(self, **data):
        super().__init__(**data)
        # Auto-generate titles if not provided
        if not self.entity_title:
            self.entity_title = self.entity_name.capitalize() + "s"
        if not self.entity_title_singular:
            singular = self.entity_name.capitalize()
            if singular.endswith("s"):
                singular = singular[:-1]  # Simple singularization
            self.entity_title_singular = singular

        # Set default table template if not provided
        if not self.table_template:
            self.table_template = f"school/{self.entity_name}_table.html"

    def render(
        self,
        request: Any,
        items: List[Dict[str, Any]],
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_asc: Optional[bool] = None,
        templates: Any = None,
        response_adapter: Optional[Callable] = None,
    ):
        """Render the table with the specified items and options"""
        # Import here to avoid circular imports
        from src.utils import prepare_table_context, response_adapter as default_adapter

        # Use provided adapter or default
        adapter = response_adapter or default_adapter

        # Prepare context
        context = prepare_table_context(
            request=request,
            table_config=self,
            items=items,
            filters=filters,
            sort_by=sort_by if sort_by is not None else self.default_sort_by,
            sort_asc=sort_asc if sort_asc is not None else self.default_sort_asc,
        )

        # Return rendered response
        return adapter(
            request=request, template_name=self.table_template, context=context, templates=templates
        )


# Predefined table configurations
def get_courses_table_config() -> TableConfig:
    """Returns the standard course table configuration"""
    return TableConfig(
        entity_name="course",
        entity_title="Courses",
        entity_title_singular="Course",
        table_template="school/courses_table.html",
        columns=[
            TableColumn(
                key="code",
                label="Code",
                sortable=True,
                filterable=True,
                type="text",
                renderer=ColumnRenderer(
                    type="custom", template="school/formatters/course_code.html"
                ),
            ),
            TableColumn(key="title", label="Title", sortable=True, filterable=True, type="text"),
            TableColumn(
                key="active",
                label="Active",
                sortable=True,
                filterable=True,
                type="boolean",
                renderer=ColumnRenderer(type="boolean"),
            ),
        ],
        default_sort_by="code",
        default_sort_asc=True,
    )

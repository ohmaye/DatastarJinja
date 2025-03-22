# Entity Page System

This project implements a generic entity management system using Pydantic models for configuration and Jinja2 templates for rendering.

## Key Components

### 1. Entity Page Template (`entity_page.html`)

A generic template that can be used for any entity in the system, providing consistent layout and features:

- Page title
- Create button
- Table with sorting and filtering
- Dialog for adding/editing
- SSE connection for real-time updates

### 2. Pydantic Model Configuration

The `TableConfig` model in `src/school/table_models.py` provides a structured way to define:

- Entity properties (name, title, etc.)
- Column configurations
- Sorting defaults
- Table template path
- Action button settings

## Usage

### 1. Define a Table Configuration

```python
from src.school.table_models import TableConfig, TableColumn, ColumnRenderer

def get_teachers_table_config() -> TableConfig:
    return TableConfig(
        entity_name="teacher",
        entity_title="Teachers", 
        entity_title_singular="Teacher",
        columns=[
            TableColumn(
                key="name",
                label="Name",
                sortable=True,
                filterable=True
            ),
            # Add more columns...
        ],
        default_sort_by="name"
    )
```

### 2. Create an Entity Route

```python
@router.get("/teachers", response_class=HTMLResponse)
async def get_teachers_page(request: Request):
    # Get data from database
    teachers_dict = get_teachers_from_db()
    
    # Get the table configuration
    table_config = get_teachers_table_config()
    table_config_dict = table_config.dict()
    
    # Return the response using the generic template
    return templates.TemplateResponse(
        request=request,
        name="components/entity_page.html",
        context={
            "entity_name": table_config.entity_name,
            "entity_title": table_config.entity_title,
            "entity_title_singular": table_config.entity_title_singular,
            "teachers": teachers_dict, 
            "filters": {}, 
            "sort_by": table_config.default_sort_by, 
            "sort_asc": table_config.default_sort_asc,
            "table_config": table_config_dict,
            "include_table": True,
            "table_template": table_config.table_template
        }
    )
```

### 3. Create a Table Template

Create a table template at the path specified in your `TableConfig` (e.g., `school/teachers_table.html`):

```html
{% from "components/data_table.html" import data_table %}

{# Using the table_config from the Pydantic model #}
{{ data_table(teachers, table_config.columns, sort_by, sort_asc, table_config.entity_name, filters) }}

<div class="bg-gray-50 px-6 py-3 border-t border-gray-200">
  <p class="text-sm text-gray-700">
    Total teachers: <span class="font-medium">{{ teachers|length }}</span>
  </p>
</div>
```

## Benefits

- **DRY Code**: No duplication of entity page templates
- **Consistent UI**: All entity pages have the same look and feel
- **Type Safety**: Pydantic models provide validation and type checking
- **Maintainability**: Changes to the entity page layout only need to be made in one place
- **Extensibility**: Easy to add new entities by just creating configurations
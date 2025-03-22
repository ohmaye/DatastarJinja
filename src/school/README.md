# Table Structure with Pydantic

This project uses Pydantic models to define and configure tables in a consistent way, making them more maintainable and easier to extend.

## Key Components

### TableColumn

Defines a single column in a data table, with properties for:

- `key`: The data field key
- `label`: Display label for the column header
- `sortable`: Whether the column can be sorted
- `filterable`: Whether the column can be filtered
- `type`: Data type (text, boolean, date, select, etc.)
- `renderer`: Optional rendering configuration
- And more...

### TableConfig

Defines the entire table configuration, including:

- `entity_name`: The name of the entity displayed in the table
- `columns`: List of TableColumn objects
- `default_sort_by`: Default sort column
- `default_sort_asc`: Default sort direction
- And more...

## Using Custom Renderers

There are two ways to customize the rendering of a column:

### 1. Using a custom template

```python
TableColumn(
    key="code",
    label="Code",
    type="text",
    renderer=ColumnRenderer(
        type="custom",
        template="school/formatters/course_code.html"
    )
)
```

The template will be included with the current context, so it can access:
- `item`: The current row data
- `column`: The current column configuration
- Other variables available in the context

### 2. Using a Python formatter function

```python
TableColumn(
    key="title",
    label="Title",
    type="text",
    renderer=ColumnRenderer(
        type="custom",
        formatter="format_title"  # Name of the function in src.school.formatters
    )
)
```

The function should be defined in `src.school.formatters` and accept a single value parameter.

## Predefined Table Configurations

For consistency, predefined table configurations are available in `table_models.py`:

```python
from src.school.table_models import get_courses_table_config

# In your route handler:
table_config = get_courses_table_config()
```

## In Templates

Pass the table configuration to your template:

```python
return templates.TemplateResponse(
    "template.html",
    {
        "request": request,
        "table_config": table_config.dict(),
        # other context variables...
    }
)
```

Then in your template:

```jinja
{% from "components/data_table.html" import data_table %}

{{ data_table(
    items=items,
    columns=table_config.columns,
    sort_by=sort_by,
    sort_asc=sort_asc,
    entity_name=table_config.entity_name,
    filters=filters
) }}
```
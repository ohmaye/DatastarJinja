from fasthtml.common import *

import db.db_spin as db_spin
from src.components.table import Column, DataTable
from src.services.table_service import TableService
from utils import render

rt = APIRouter(prefix="/test")


@rt("/tbl")
async def get(req):
    table_service = TableService(db_spin)

    # Get table data
    data = await table_service.get_table_data(
        "student",
        sort_by=req.query_params.get("sort_by"),
        sort_order=req.query_params.get("order", "asc"),
    )

    # Create table component
    table = DataTable(
        id="student",
        columns=[
            Column("First Name", "firstName"),
            Column("Last Name", "lastName"),
            Column("Email", "email"),
            Column("Level", "level"),
            Column("Program", "program"),
            Column("Active", "active"),
        ],
        data=data.to_dict("records"),
        sort_by=req.query_params.get("sort_by"),
        sort_order=req.query_params.get("order", "asc"),
        on_sort=lambda col: f"/api/sort?column={col}",
        row_actions=[
            {
                "label": "Edit",
                "props": {"hx_get": "/api/edit/{id}", "cls": "btn btn-xs"},
            },
        ],
    )

    return render(req, table.render())

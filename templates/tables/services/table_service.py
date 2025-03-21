# services/table_service.py
from typing import Optional

import pandas as pd


class TableService:
    def __init__(self, db_connection):
        self.db = db_connection

    async def get_table_data(
        self,
        table_name: str,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        filters: Optional[dict] = None,
    ) -> pd.DataFrame:
        query = f"SELECT * FROM {table_name}"

        if filters:
            query += " WHERE " + " AND ".join(
                f"{k} = '{v}'" for k, v in filters.items()
            )

        if sort_by:
            query += f" ORDER BY {sort_by} {sort_order}"

        return self.db.run(query)

    async def apply_filters(self, df: pd.DataFrame, filters: dict) -> pd.DataFrame:
        for key, value in filters.items():
            if value:
                df = df[df[key].str.contains(value, case=False, na=False)]
        return df

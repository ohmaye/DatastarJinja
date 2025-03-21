# components/table.py
from dataclasses import dataclass
from typing import Callable, List, Optional

from fasthtml.common import *


@dataclass
class Column:
    name: str
    key: str
    sortable: bool = True
    filterable: bool = True
    render: Optional[Callable] = None


class DataTable:
    def __init__(
        self,
        id: str,
        columns: List[Column],
        data: List[dict],
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        on_sort: Optional[Callable] = None,
        on_filter: Optional[Callable] = None,
        row_actions: Optional[List[dict]] = None,
    ):
        self.id = id
        self.columns = columns
        self.data = data
        self.sort_by = sort_by
        self.sort_order = sort_order
        self.on_sort = on_sort
        self.on_filter = on_filter
        self.row_actions = row_actions

    def render(self) -> Div:
        return Div(cls="border border-gray-200 rounded-box shadow-lg overflow-hidden")(
            Table(cls="table table-xs lg:table-md relative", id=self.id)(
                self._render_header(),
                self._render_body(),
                # self._render_footer()
            )
        )

    def _render_header(self) -> Thead:
        return Thead(cls="sticky top-0 z-10 bg-gray-100")(
            Tr(
                *[
                    Th(cls="text-gray-600 font-semibold")(
                        col.name,
                        data_on_click=f"$sort_by='{col.key}', @get('/api/sort')"
                        if col.sortable
                        else None,
                        cls="cursor-pointer hover:bg-indigo-100"
                        if col.sortable
                        else None,
                    )
                    for col in self.columns
                ],
                *([Th("Actions")] if self.row_actions else []),
            )
        )

    def _render_body(self) -> Tbody:
        return Tbody(*[self._render_row(row) for row in self.data])

    def _render_row(self, row: dict) -> Tr:
        return Tr(cls="hover:bg-gray-100")(
            *[
                Td(col.render(row) if col.render else row.get(col.key))
                for col in self.columns
            ],
            *(
                [
                    Td(
                        *[
                            Button(action["label"], **action["props"])
                            for action in self.row_actions
                        ]
                    )
                ]
                if self.row_actions
                else []
            ),
        )

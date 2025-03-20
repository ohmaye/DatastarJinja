# School Routes
from dataclasses import asdict
from uuid import UUID

from fasthtml.common import *

import db.db_school as db_school
from db.models import Timeslot
from utils import render

rt = APIRouter(prefix="/school")

# Globals
current_sort_by = None
current_sort_ascending = True
current_filter_by = None


def timeslot_empty_form():
    cls_input = "input input-bordered input-info w-full max-w-xs mb-3 mt-1"

    html = Div(
        Dialog(
            data_ref="timeslot_dialog",
            data_on_load="$timeslot_dialog.show()",
            cls="modal",
            **{
                "data-on-keydown__window": "evt.key == 'Escape' && $timeslot_dialog.close()",
            },
        )(
            Div(
                data_on_click="$timeslot_dialog.close()",
                cls="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 flex items-center justify-center",
            ),
            Form(cls="modal-box form-control z-100")(
                H3("Edit Timeslot", cls="text-lg font-bold my-4"),
                Div(cls="flex flex-col px-4 border border-indigo-100 rounded-lg")(
                    Input(name="id", cls="invisible"),
                    Label("Weekday", cls="label"),
                    Input(name="weekday", cls=cls_input),
                    Label("Start Time", cls="label"),
                    Input(name="start_time", cls=cls_input),
                    Label("End Time", cls="label"),
                    Input(name="end_time", cls=cls_input),
                    Label("Active", cls="label"),
                    Input(type="checkbox", name="active", cls="checkbox"),
                    Div(cls="flex flex-row justify-between my-6")(
                        Button("Cancel", cls="btn"),
                        Button(
                            "Save",
                            type="submit",
                            hx_put="/school/timeslots",
                            cls="btn btn-primary",
                        ),
                    ),
                ),
            ),
        ),
    )
    return html


def render_row(timeslot):
    return Tr(cls=" hover:bg-gray-200")(
        Td(
            Button(
                "Edit",
                hx_get=f"/school/timeslots/edit?timeslot={timeslot}",
                hx_target="#main",
                hx_swap="afterbegin",
                cls="btn btn-xs btn-outline",
            )
        ),
        Td(timeslot.weekday),
        Td(timeslot.start_time),
        Td(timeslot.end_time),
        Td(
            Input(
                type="checkbox", checked=timeslot.active, disabled=True, cls="checkbox"
            )
        ),
        Td(
            Button(
                "Delete",
                hx_delete=f"/school/timeslots/{timeslot.id}",
                hx_target="#main",
                # hx_confirm="Are you sure you want to delete?",
                cls="btn btn-xs btn-secondary",
            )
        ),
    )


def filter():
    return Th(Input("", type="text", cls="border border-blue-200 w-24"))


def timeslot_table(timeslots):
    html = (
        Button(
            "Create New Timeslot",
            hx_post="/school/timeslots",
            hx_target="#main",
            hx_swap="afterbegin",
            cls="btn right ml-4 my-2 shadow-md",
        ),
        Div(cls="ml-4 border border-gray-200 rounded-box shadow-lg")(
            Table(cls="table")(
                Tr(
                    Th(""),
                    Th(
                        "Weekday",
                        hx_get='/school/timeslots?sort_by="weekday"',
                        hx_target="#main",
                        cls="hover:bg-gray-200",
                    ),
                    Th(
                        "Start Time",
                        hx_get='/school/timeslots?sort_by="start_time"',
                        hx_target="#main",
                        cls="hover:bg-gray-200",
                    ),
                    Th(
                        "End Time",
                        hx_get='/school/timeslots?sort_by="end_time"',
                        hx_target="#main",
                        cls="hover:bg-gray-200",
                    ),
                    Th(
                        "Active",
                        hx_get='/school/timeslots?sort_by="active"',
                        hx_target="#main",
                        cls="hover:bg-gray-200",
                    ),
                    Th(""),
                ),
                Tr(
                    Th(),
                    filter(),
                    filter(),
                    filter(),
                    Th(),
                    Th(),
                ),
                *[render_row(timeslot) for timeslot in timeslots],
            ),
        ),
    )
    return html


# List all timeslots (table with rows + Edit/Delete)
@rt("/timeslots")
def get(req, sort_by: str = None, filter_by: str = None):
    db_timeslots = db_school.get_all("timeslot")
    if filter_by is not None:
        db_timeslots = db_timeslots[
            db_timeslots["weekday"].str.contains(filter_by, case=False, na=False)
        ]
    if sort_by is not None:
        db_timeslots = db_timeslots.sort_values(sort_by.strip('"'))
    timeslots = [
        Timeslot(**timeslot.to_dict()) for _, timeslot in db_timeslots.iterrows()
    ]
    html = timeslot_table(timeslots)
    return render(req, html)


@rt("/timeslots/edit")
def get(timeslot: str, req):
    timeslot = eval(timeslot)
    form = timeslot_empty_form()
    fill_form(form, timeslot)
    return render(req, form)


# Create New Timeslot
@rt("/timeslots")
def post(req):
    new_timeslot = db_school.create("timeslot")
    timeslot = Timeslot(**new_timeslot.to_dict())
    form = timeslot_empty_form()
    fill_form(form, timeslot)
    return render(req, form)


# UPDATE Timeslot
@rt("/timeslots")
def put(timeslot: Timeslot, req):
    db_school.update("timeslot", asdict(timeslot))
    return HtmxResponseHeaders(redirect="/school/timeslots")


# DELETE Timeslot
@rt("/timeslots/{id}")
def delete(id: str, req):
    db_school.delete("timeslot", id)
    return HtmxResponseHeaders(redirect="/school/timeslots")

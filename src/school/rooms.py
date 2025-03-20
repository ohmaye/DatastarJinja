# School Routes
from dataclasses import asdict
from uuid import UUID

from fasthtml.common import *

import db.db_school as db_school
from db.models import Room
from utils import render

rt = APIRouter(prefix="/school")

# Globals
current_sort_by = None
current_sort_ascending = True
current_filter_by = None


def room_empty_form():
    cls_input = "input input-bordered input-info w-full max-w-xs mb-3 mt-1"

    html = Div(
        Dialog(
            data_ref="room_dialog",
            data_on_load="$room_dialog.show()",
            cls="modal",
            **{
                "data-on-keydown__window": "evt.key == 'Escape' && $room_dialog.close()",
            },
        )(
            Div(
                data_on_click="$room_dialog.close()",
                cls="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 flex items-center justify-center",
            ),
            Form(cls="modal-box form-control z-100")(
                H3("Edit Room", cls="text-lg font-bold my-4"),
                Div(cls="flex flex-col px-4 border border-indigo-100 rounded-lg")(
                    Input(name="id", cls="invisible"),
                    Label("Name", cls="label"),
                    Input(name="name", cls=cls_input),
                    Label("Type", cls="label"),
                    Input(name="type", cls=cls_input),
                    Label("Capacity", cls="label"),
                    Input(type="number", name="capacity", cls=cls_input),
                    Label("Active", cls="label"),
                    Input(type="checkbox", name="active", cls="checkbox"),
                    Div(cls="flex flex-row justify-between my-6")(
                        Button(cls="btn")("Cancel"),
                        Button(
                            type="submit",
                            hx_put="/school/rooms",
                            cls="btn btn-primary",
                        )("Save"),
                    ),
                ),
            ),
        ),
    )
    return html


def render_row(room):
    # print("ROW: ", row.to_dict())
    return Tr(
        Td(
            Button(
                "Edit",
                hx_get=f"/school/rooms/edit?room={room}",
                hx_target="#main",
                hx_swap="afterbegin",
                cls="btn btn-xs btn-outline",
            )
        ),
        Td(room.name),
        Td(room.type),
        Td(room.capacity),
        Td(Input(type="checkbox", checked=room.active, disabled=True, cls="checkbox")),
        Td(
            Button(
                "Delete",
                hx_delete=f"/school/rooms/{room.id}",
                hx_target="#main",
                # hx_confirm="Are you sure you want to delete?",
                cls="btn btn-xs btn-secondary",
            )
        ),
        cls=" hover:bg-gray-200",
    )


def filter():
    return Th(Input("", type="text", cls="border border-blue-200 w-24"))


def room_table(rooms):
    html = (
        Button(
            "Create New Room",
            hx_post="/school/rooms",
            hx_target="#main",
            hx_swap="afterbegin",
            cls="btn right ml-4 my-2 shadow-md",
        ),
        Div(
            Table(
                Tr(
                    Th(""),
                    Th(
                        "Name",
                        hx_get='/school/rooms?sort_by="name"',
                        hx_target="#main",
                        cls="hover:bg-gray-200",
                    ),
                    Th(
                        "Type",
                        hx_get='/school/rooms?sort_by="type"',
                        hx_target="#main",
                        cls="hover:bg-gray-200",
                    ),
                    Th(
                        "Capacity",
                        hx_get='/school/rooms?sort_by="capacity"',
                        hx_target="#main",
                        cls="hover:bg-gray-200",
                    ),
                    Th(
                        "Active",
                        hx_get='/school/rooms?sort_by="active"',
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
                *[render_row(room) for room in rooms],
                cls="table",
            ),
            cls="ml-4 border border-gray-200 rounded-box shadow-lg",
        ),
    )
    return html


# List all rooms (table with rows + Edit/Delete)
@rt("/rooms")
def get(req, sort_by: str = None, filter_by: str = None):
    db_rooms = db_school.get_all("room")
    if filter_by is not None:
        db_rooms = db_rooms[
            db_rooms["name"].str.contains(filter_by, case=False, na=False)
        ]
    if sort_by is not None:
        db_rooms = db_rooms.sort_values(sort_by.strip('"'))
    rooms = [Room(**room.to_dict()) for _, room in db_rooms.iterrows()]
    html = room_table(rooms)
    return render(req, html)


@rt("/rooms/edit")
def get(room: str, req):
    room = eval(room)
    form = room_empty_form()
    fill_form(form, room)
    return render(req, form)


# Create New Course
@rt("/rooms")
def post(req):
    new_room = db_school.create("room")
    room = Room(**new_room.to_dict())
    form = room_empty_form()
    fill_form(form, room)
    return render(req, form)


# UPDATE Course
@rt("/rooms")
def put(room: Room, req):
    db_school.update("room", asdict(room))
    return HtmxResponseHeaders(redirect="/school/rooms")


# DELETE Course
@rt("/rooms/{id}")
def delete(id: str, req):
    db_school.delete("room", id)
    return HtmxResponseHeaders(redirect="/school/rooms")

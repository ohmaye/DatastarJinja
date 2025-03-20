# School Routes
from dataclasses import asdict
from uuid import UUID

from fasthtml.common import *

import db.db_school as db_school
from db.models import Teacher
from utils import render

rt = APIRouter(prefix="/school")

# Globals
current_sort_by = None
current_sort_ascending = True
current_filter_by = None


def teacher_empty_form():
    cls_input = "input input-bordered input-info w-full max-w-xs mb-3 mt-1"

    html = Div(
        Dialog(
            data_ref="teacher_dialog",
            data_on_load="$teacher_dialog.show()",
            cls="modal",
            **{
                "data-on-keydown__window": "evt.key == 'Escape' && $teacher_dialog.close()",
            },
        )(
            Div(
                data_on_click="$teacher_dialog.close()",
                cls="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 flex items-center justify-center",
            ),
            Form(cls="modal-box form-control z-100")(
                H3("Edit Teacher", cls="text-lg font-bold my-4"),
                Div(cls="flex flex-col px-4 border border-indigo-100 rounded-lg")(
                    Input(name="id", cls="invisible"),
                    Label("Name", cls="label"),
                    Input(name="name", cls=cls_input),
                    Label("Name JP", cls="label"),
                    Input(name="nameJP", cls=cls_input),
                    Label("email", cls="label"),
                    Input(name="email", cls=cls_input),
                    Label("Note", cls="label"),
                    Input(name="note", cls=cls_input),
                    Label("Active", cls="label"),
                    Input(type="checkbox", name="active", cls="checkbox"),
                    Div(cls="flex flex-row justify-between my-6")(
                        Button("Cancel", cls="btn"),
                        Button(
                            "Save",
                            type="submit",
                            hx_put="/school/teachers",
                            cls="btn btn-primary",
                        ),
                    ),
                ),
            ),
        ),
    )
    return html


def render_row(teacher):
    # print("ROW: ", row.to_dict())
    return Tr(cls=" hover:bg-gray-200")(
        Td(
            Button(
                "Edit",
                hx_get=f"/school/teachers/edit?teacher={teacher}",
                hx_target="#main",
                hx_swap="afterbegin",
                cls="btn btn-xs btn-outline",
            )
        ),
        Td(teacher.name),
        Td(teacher.nameJP),
        Td(teacher.email),
        Td(teacher.note),
        Td(
            Input(
                type="checkbox", checked=teacher.active, disabled=True, cls="checkbox"
            )
        ),
        Td(
            Button(
                "Delete",
                hx_delete=f"/school/teachers/{teacher.id}",
                hx_target="#main",
                # hx_confirm="Are you sure you want to delete?",
                cls="btn btn-xs btn-secondary",
            )
        ),
    )


def filter():
    return Th(Input("", type="text", cls="border border-blue-200 w-24"))


def teacher_table(teachers):
    html = (
        Button(
            "Create New Teacher",
            hx_post="/school/teachers",
            hx_target="#main",
            hx_swap="afterbegin",
            cls="btn right ml-4 my-2 shadow-md",
        ),
        Div(cls="ml-4 border border-gray-200 rounded-box shadow-lg")(
            Table(cls="table")(
                Tr(
                    Th(""),
                    Th(
                        "Name",
                        hx_get='/school/teachers?sort_by="name"',
                        hx_target="#main",
                        cls="hover:bg-gray-200",
                    ),
                    Th(
                        "Name JP",
                        hx_get='/school/teachers?sort_by="nameJP"',
                        hx_target="#main",
                        cls="hover:bg-gray-200",
                    ),
                    Th(
                        "email",
                        hx_get='/school/teachers?sort_by="email"',
                        hx_target="#main",
                        cls="hover:bg-gray-200",
                    ),
                    Th(
                        "Note",
                        hx_get='/school/teachers?sort_by="note"',
                        hx_target="#main",
                        cls="hover:bg-gray-200",
                    ),
                    Th(
                        "Active",
                        hx_get='/school/teachers?sort_by="active"',
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
                    filter(),
                    Th(),
                    Th(),
                ),
                *[render_row(teacher) for teacher in teachers],
            ),
        ),
    )
    return html


# List all teachers (table with rows + Edit/Delete)
@rt("/teachers")
def get(req, sort_by: str = None, filter_by: str = None):
    db_teachers = db_school.get_all("teacher")
    if filter_by is not None:
        db_teachers = db_teachers[
            db_teachers["name"].str.contains(filter_by, case=False, na=False)
        ]
    if sort_by is not None:
        db_teachers = db_teachers.sort_values(sort_by.strip('"'))
    teachers = [Teacher(**teacher.to_dict()) for _, teacher in db_teachers.iterrows()]
    html = teacher_table(teachers)
    return render(req, html)


@rt("/teachers/edit")
def get(teacher: str, req):
    teacher = eval(teacher)
    form = teacher_empty_form()
    fill_form(form, teacher)
    return render(req, form)


# Create New Course
@rt("/teachers")
def post(req):
    new_teacher = db_school.create("teacher")
    teacher = Teacher(**new_teacher.to_dict())
    form = teacher_empty_form()
    fill_form(form, teacher)
    return render(req, form)


# UPDATE Course
@rt("/teachers")
def put(teacher: Teacher, req):
    db_school.update("teacher", asdict(teacher))
    return HtmxResponseHeaders(redirect="/school/teachers")


# DELETE Course
@rt("/teachers/{id}")
def delete(id: str, req):
    db_school.delete("teacher", id)
    return HtmxResponseHeaders(redirect="/school/teachers")

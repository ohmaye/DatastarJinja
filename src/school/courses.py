# School Routes
from dataclasses import asdict
from uuid import UUID

from fasthtml.common import *

import db.db_school as db_school
from db.models import Course
from utils import render

rt = APIRouter(prefix="/school")

# Globals
current_sort_by = None
current_sort_ascending = True
current_filter_by = None


def course_empty_form():
    cls_input = "input input-bordered input-info w-full max-w-xs mb-3 mt-1"

    html = Div(
        Dialog(
            data_ref="course_dialog",
            data_on_load="$course_dialog.show()",
            cls="modal",
            **{
                "data-on-keydown__window": "evt.key == 'Escape' && $course_dialog.close()",
            },
        )(
            Div(
                data_on_click="$course_dialog.close()",
                cls="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 flex items-center justify-center",
            ),
            Form(cls="modal-box form-control z-100")(
                H3("Edit Course", cls="text-lg font-bold my-4"),
                Div(cls="flex flex-col px-4 border border-indigo-100 rounded-lg")(
                    Input(name="id", cls="invisible"),
                    Label("Code", cls="label"),
                    Input(name="code", cls=cls_input),
                    Label("Title", cls="label"),
                    Input(name="title", cls=cls_input),
                    Label("Active", cls="label"),
                    Input(type="checkbox", name="active", cls="checkbox"),
                    Div(cls="flex flex-row justify-between my-6")(
                        Button(cls="btn")("Cancel"),
                        Button(
                            type="submit",
                            hx_put="/school/courses",
                            cls="btn btn-primary",
                        )("Save"),
                    ),
                ),
            ),
        ),
    )
    return html


def render_row(course):
    return Tr(cls=" hover:bg-gray-200")(
        Td(
            Button(
                "Edit",
                hx_get=f"/school/courses/edit?course={course}",
                hx_target="#main",
                hx_swap="afterbegin",
                cls="btn btn-xs btn-outline",
            )
        ),
        Td(course.code),
        Td(course.title),
        Td(
            Input(type="checkbox", checked=course.active, disabled=True, cls="checkbox")
        ),
        Td(
            Button(
                "Delete",
                hx_delete=f"/school/courses/{course.id}",
                hx_target="#main",
                # hx_confirm="Are you sure you want to delete?",
                cls="btn btn-xs btn-secondary",
            )
        ),
    )


def filter():
    return Th(Input("", type="text", cls="border border-blue-200 w-24"))


def course_table(courses):
    html = (
        Button(
            "Create New Course",
            hx_post="/school/courses",
            hx_target="#main",
            hx_swap="afterbegin",
            cls="btn right ml-4 my-2 shadow-md",
        ),
        Div(cls="ml-4 border border-gray-200 rounded-box shadow-lg")(
            Table(cls="table")(
                Tr(
                    Th(""),
                    Th(
                        "Code",
                        hx_get='/school/courses?sort_by="code"',
                        hx_target="#main",
                        cls="hover:bg-gray-200",
                    ),
                    Th(
                        "Title",
                        hx_get='/school/courses?sort_by="title"',
                        hx_target="#main",
                        cls="hover:bg-gray-200",
                    ),
                    Th(
                        "Active",
                        hx_get='/school/courses?sort_by="active"',
                        hx_target="#main",
                        cls="hover:bg-gray-200",
                    ),
                    Th(""),
                ),
                Tr(
                    Th(),
                    filter(),
                    filter(),
                    Th(),
                    Th(),
                ),
                *[render_row(course) for course in courses],
            ),
        ),
    )
    return html


# List all courses (table with rows + Edit/Delete)
@rt("/courses")
def get(req, sort_by: str = None, filter_by: str = None):
    db_courses = db_school.get_all("course")
    if filter_by is not None:
        db_courses = db_courses[
            db_courses["code"].str.contains(filter_by, case=False, na=False)
        ]
    if sort_by is not None:
        db_courses = db_courses.sort_values(sort_by.strip('"'))
    courses = [Course(**course.to_dict()) for _, course in db_courses.iterrows()]
    html = course_table(courses)
    return render(req, html)


@rt("/courses/edit")
def get(course: str, req):
    course = eval(course)
    form = course_empty_form()
    fill_form(form, course)
    return render(req, form)


# Create New Course
@rt("/courses")
def post(req):
    new_course = db_school.create("course")
    course = Course(**new_course.to_dict())
    form = course_empty_form()
    fill_form(form, course)
    return render(req, form)


# UPDATE Course
@rt("/courses")
def put(course: Course, req):
    db_school.update("course", asdict(course))
    return HtmxResponseHeaders(redirect="/school/courses")


# DELETE Course
@rt("/courses/{id}")
def delete(id: str, req):
    db_school.delete("course", id)
    return HtmxResponseHeaders(redirect="/school/courses")

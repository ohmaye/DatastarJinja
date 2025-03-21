import uuid
import asyncio
from dataclasses import asdict
from typing import Dict, List, Optional, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Form, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datastar_py.responses import DatastarFastAPIResponse

import db.db_school as db_school
from db.models import Course

router = APIRouter(prefix="/school", tags=["courses"])
templates = Jinja2Templates(directory="templates")


# Helper functions
def parse_filter_params(params: Dict[str, str]) -> Dict[str, str]:
    """Extract filter parameters from query params"""
    filters = {}
    for key, value in params.items():
        if key.startswith("filter_") and value:
            filter_name = key.replace("filter_", "")
            filters[filter_name] = value
    return filters


def filter_courses(courses: List[Dict[str, Any]], filters: Dict[str, str]) -> List[Dict[str, Any]]:
    """Apply filters to courses list"""
    filtered_courses = courses

    for key, value in filters.items():
        if key == "code" and value:
            filtered_courses = [c for c in filtered_courses if value.lower() in c["code"].lower()]
        elif key == "title" and value:
            filtered_courses = [c for c in filtered_courses if value.lower() in c["title"].lower()]
        elif key == "active":
            is_active = value.lower() == "true"
            filtered_courses = [c for c in filtered_courses if c["active"] == is_active]

    return filtered_courses


def sort_courses(
    courses: List[Dict[str, Any]], sort_by: Optional[str], sort_asc: bool
) -> List[Dict[str, Any]]:
    """Sort courses by specified field"""
    if not sort_by:
        return courses

    reverse = not sort_asc
    return sorted(courses, key=lambda x: x.get(sort_by, ""), reverse=reverse)


# Success and error messages
def create_success_message(sse):
    html = """
    <div class="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-4" role="alert">
        <p>Course operation completed successfully.</p>
    </div>
    """
    return sse.fragment(html)


def create_error_message(sse, error_msg):
    html = f"""
    <div class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4" role="alert">
        <p>Error: {error_msg}</p>
    </div>
    """
    return sse.fragment(html)


# Routes
@router.get("/courses", response_class=HTMLResponse)
async def get_courses_page(request: Request):
    """Render the courses main page"""
    # Get all courses from the database
    db_courses = db_school.get_all("course")
    courses = [Course(**course.to_dict()) for _, course in db_courses.iterrows()]
    courses_dict = [asdict(course) for course in courses]

    return templates.TemplateResponse(
        request=request,
        name="school/courses.html",
        context={"courses": courses_dict, "filters": {}, "sort_by": None, "sort_asc": True},
    )


@router.get("/courses/new", response_class=HTMLResponse)
async def get_new_course_form(request: Request):
    """Get an empty course form for creating a new course"""
    return templates.TemplateResponse(
        request=request, name="school/course_form.html", context={"course": None}
    )


@router.get("/courses/data", response_class=HTMLResponse)
async def get_courses_data(
    request: Request, sort_by: Optional[str] = None, sort_asc: Optional[bool] = True
):
    """Get courses data for the table partial using server-side processing"""
    # Get filter parameters
    filters = parse_filter_params(dict(request.query_params))

    # Get all courses from the database
    db_courses = db_school.get_all("course")
    courses = [Course(**course.to_dict()) for _, course in db_courses.iterrows()]
    courses_dict = [asdict(course) for course in courses]

    # Apply filters
    filtered_courses = filter_courses(courses_dict, filters)

    # Apply sorting
    sorted_courses = sort_courses(filtered_courses, sort_by, sort_asc)

    # Return the table HTML
    return templates.TemplateResponse(
        request=request,
        name="school/courses_table.html",
        context={
            "courses": sorted_courses,
            "filters": filters,
            "sort_by": sort_by,
            "sort_asc": sort_asc,
        },
    )


@router.get("/courses/stream")
async def stream_courses(request: Request):
    """Stream courses data using SSE for real-time updates"""

    async def generate_updates(sse):
        # Create a fragment with the data that will trigger an update on a timer
        while True:
            if await request.is_disconnected():
                break

            yield sse.merge_fragments(['<div data-signal-update="coursesRefresh:true"></div>'])

            # Wait 5 seconds before sending the next update
            await asyncio.sleep(5)

    return DatastarFastAPIResponse(generate_updates)


@router.get("/courses/{course_id}", response_class=HTMLResponse)
async def get_course(request: Request, course_id: str):
    """Get a single course for editing"""
    try:
        course_data = db_school.get("course", course_id)
        if course_data.empty:
            raise HTTPException(status_code=404, detail="Course not found")

        course = Course(**course_data.iloc[0].to_dict())
        course_dict = asdict(course)

        return templates.TemplateResponse(
            request=request, name="school/course_form.html", context={"course": course_dict}
        )
    except Exception as e:
        error_msg = str(e)

        async def error_response(sse):
            yield create_error_message(sse, error_msg)

        return DatastarFastAPIResponse(error_response)


@router.post("/courses", response_class=HTMLResponse)
async def create_course(
    request: Request, code: str = Form(...), title: str = Form(...), active: bool = Form(False)
):
    """Create a new course"""
    try:
        # Create new course in the database
        new_course_data = db_school.create("course")

        # Update with form data
        course_id = str(new_course_data["id"])
        update_data = {"id": course_id, "code": code, "title": title, "active": active}
        db_school.update("course", update_data)

        # Return success message
        async def success_response(sse):
            yield create_success_message(sse)

        return DatastarFastAPIResponse(success_response)
    except Exception as e:
        # Return error message
        error_msg = str(e)

        async def error_response(sse):
            yield create_error_message(sse, error_msg)

        return DatastarFastAPIResponse(error_response)


@router.put("/courses/{course_id}", response_class=HTMLResponse)
async def update_course(
    request: Request,
    course_id: str,
    code: str = Form(...),
    title: str = Form(...),
    active: bool = Form(False),
):
    """Update an existing course"""
    try:
        # Update course in the database
        update_data = {"id": course_id, "code": code, "title": title, "active": active}
        db_school.update("course", update_data)

        # Return success message
        async def success_response(sse):
            yield create_success_message(sse)

        return DatastarFastAPIResponse(success_response)
    except Exception as e:
        # Return error message
        error_msg = str(e)

        async def error_response(sse):
            yield create_error_message(sse, error_msg)

        return DatastarFastAPIResponse(error_response)


@router.delete("/courses/{course_id}", response_class=HTMLResponse)
async def delete_course(request: Request, course_id: str):
    """Delete a course"""
    try:
        # Delete course from the database
        db_school.delete("course", course_id)

        # Return success message
        async def success_response(sse):
            yield create_success_message(sse)

        return DatastarFastAPIResponse(success_response)
    except Exception as e:
        # Return error message
        error_msg = str(e)

        async def error_response(sse):
            yield create_error_message(sse, error_msg)

        return DatastarFastAPIResponse(error_response)

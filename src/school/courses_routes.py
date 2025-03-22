import uuid
import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Request, HTTPException, Form, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.db import db_school
from src.utils import prepare_table_context, response_adapter
from src.school.table_models import get_courses_table_config
from src.school.models import Course
from pydantic import BaseModel, Field, ValidationError

# Create router for school module
router = APIRouter(prefix="/school", tags=["school"])

# Get the templates directory path
templates_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates"
)
templates = Jinja2Templates(directory=templates_dir)


# Helper functions
def parse_filter_params(
    q: Optional[str] = None, active_only: Optional[bool] = False
) -> Dict[str, Any]:
    """Parse filter parameters from request query params"""
    filters = {}

    # Add text search filter if provided
    if q:
        filters["q"] = q

    # Add active filter if true
    if active_only:
        filters["active"] = True

    return filters


def filter_courses(courses: List[Any], filters: Dict[str, Any]) -> List[Any]:
    """Filter courses based on the filter parameters"""
    filtered_courses = courses.copy()

    # Handle text search across multiple fields
    if "q" in filters and filters["q"]:
        query = filters["q"].lower()
        filtered_courses = [
            course
            for course in filtered_courses
            if (
                str(course.get("code", "")).lower().find(query) != -1
                or str(course.get("title", "")).lower().find(query) != -1
            )
        ]

    # Handle active filter
    if "active" in filters:
        active_value = filters["active"]
        filtered_courses = [
            course for course in filtered_courses if course.get("active") == active_value
        ]

    return filtered_courses


def sort_courses(
    courses: List[Any], sort_by: Optional[str], sort_asc: Optional[bool] = True
) -> List[Any]:
    """Sort courses based on the sort parameters"""
    if not sort_by:
        return courses

    def get_value(item, key):
        """Get value from either a dictionary or an object"""
        if isinstance(item, dict):
            return item.get(key, "")
        else:
            return getattr(item, key, "")

    # Handle special case for code (case-insensitive sorting)
    if sort_by == "code":
        sorted_courses = sorted(
            courses, key=lambda c: str(get_value(c, sort_by)).lower(), reverse=not sort_asc
        )
    else:
        sorted_courses = sorted(courses, key=lambda c: get_value(c, sort_by), reverse=not sort_asc)

    return sorted_courses


# Success and error messages
def create_success_message() -> str:
    """Create a success message HTML snippet"""
    return """
    <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">
        <strong class="font-bold">Success!</strong>
        <span class="block sm:inline"> The operation was completed successfully.</span>
    </div>
    """


def create_error_message(error_msg: str = "") -> str:
    """Create an error message HTML snippet"""
    return f"""
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
        <strong class="font-bold">Error!</strong>
        <span class="block sm:inline"> {error_msg}</span>
    </div>
    """


# Define a Pydantic model for course creation and update
class CourseCreate(BaseModel):
    """Schema for course creation"""

    code: str = Field(..., description="The course code")
    title: str = Field(..., description="The course title")
    active: bool = Field(False, description="Whether the course is active")


# Routes
@router.get("/courses", response_class=HTMLResponse)
async def get_courses_page(request: Request):
    """Render the courses main page"""
    # Get all courses from the database
    db_courses = db_school.get_all("course")

    # Convert DataFrame rows to Course models
    courses = []
    for index, row in db_courses.iterrows():
        course_dict = row.to_dict()
        # Ensure ID is a string
        if "id" in course_dict:
            course_dict["id"] = str(course_dict["id"])
        # Create a Course model and convert to dict for template rendering
        course = Course.from_db_row(course_dict)
        courses.append(course.to_response_dict())

    # Use the Pydantic model for table configuration
    table_config = get_courses_table_config()

    # Use the entity_page.html template directly
    context = prepare_table_context(request=request, table_config=table_config, items=courses)

    # The entity_page template is different from the table template
    return response_adapter(
        request=request,
        template_name="components/entity_page.html",
        context=context,
        templates=templates,
        url="/school/courses",
    )


@router.get("/courses/new", response_class=HTMLResponse)
async def get_new_course_form(request: Request):
    """Return the empty course form"""
    # For the form, we just need an empty dict, not a validated Course model
    # This avoids validation errors for the empty form
    empty_course = {"id": "", "code": "", "title": "", "active": False}

    # Return empty form for creating a new course
    return response_adapter(
        request=request,
        template_name="school/course_form.html",
        context={"course": empty_course},
        templates=templates,
        url="/school/courses/new",
    )


@router.get("/courses/data", response_class=HTMLResponse)
async def get_courses_data(
    request: Request,
    q: Optional[str] = Query(None, description="Search query for filtering courses"),
    active_only: Optional[bool] = Query(False, description="Filter to show only active courses"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_asc: Optional[bool] = Query(True, description="Sort in ascending order"),
):
    """Get filtered and sorted courses for the table"""
    # Filter and sort the courses based on the request parameters
    db_courses = db_school.get_all("course")

    # Convert DataFrame rows to Course models
    courses = []
    for index, row in db_courses.iterrows():
        course_dict = row.to_dict()
        # Ensure ID is a string
        if "id" in course_dict:
            course_dict["id"] = str(course_dict["id"])
        # Create a Course model and convert to dict
        course = Course.from_db_row(course_dict)
        courses.append(course.to_response_dict())

    # Apply filters if provided
    filters = parse_filter_params(q=q, active_only=active_only)
    if filters:
        courses = filter_courses(courses, filters)

    # Apply sorting if provided
    if sort_by:
        courses = sort_courses(courses, sort_by, sort_asc)

    # Get the table configuration
    table_config = get_courses_table_config()

    # Construct URL with query parameters if they exist
    url_parts = ["/school/courses/data"]
    query_params = []

    if q:
        query_params.append(f"q={q}")
    if active_only:
        query_params.append("active_only=true")
    if sort_by:
        query_params.append(f"sort_by={sort_by}")
        query_params.append(f"sort_asc={'true' if sort_asc else 'false'}")

    if query_params:
        url = f"{url_parts[0]}?{'&'.join(query_params)}"
    else:
        url = url_parts[0]

    # Use the table_config's render method for simplified rendering
    return table_config.render(
        request=request,
        items=courses,
        filters=filters,
        sort_by=sort_by,
        sort_asc=sort_asc,
        templates=templates,
        url=url,
    )


@router.get("/courses/{course_id}", response_class=HTMLResponse)
async def get_course(request: Request, course_id: str):
    """Get a single course for editing"""
    try:
        course_data = db_school.get("course", course_id)
        if course_data.empty:
            raise HTTPException(status_code=404, detail="Course not found")

        # Create a Course Pydantic model from the database data
        # This will validate the data as it's loaded
        course = Course.from_db_row(course_data.iloc[0].to_dict())

        return response_adapter(
            request=request,
            template_name="school/course_form.html",
            context={"course": course.to_response_dict()},
            templates=templates,
            url=f"/school/courses/{course_id}",
        )
    except ValueError as validation_error:
        # This would catch Pydantic validation errors specifically
        error_html = create_error_message(f"Data validation error: {str(validation_error)}")
        return response_adapter(
            request=request,
            template_name="error_message.html",
            context={"message_html": error_html},
            templates=templates,
            status_code=400,
        )
    except Exception as e:
        error_html = create_error_message(str(e))
        return response_adapter(
            request=request,
            template_name="error_message.html",
            context={"message_html": error_html},
            templates=templates,
            status_code=400,
        )


@router.post("/courses", response_class=HTMLResponse)
async def create_course(
    request: Request,
    form_data: CourseCreate = Depends(
        lambda request: CourseCreate(
            code=request.form.get("code"),
            title=request.form.get("title"),
            active=request.form.get("active") == "true" or request.form.get("active") == "on",
        )
    ),
):
    """Create a new course with Pydantic validation"""
    try:
        # Create a new course ID
        course_id = str(uuid.uuid4())

        # Create a validated Course model instance
        new_course = Course(id=course_id, **form_data.dict())

        # Save the course to the database using the model's serialization method
        db_school.create("course", new_course.to_db_dict())

        # Generate success message
        success_html = create_success_message()

        # Return the success message
        return response_adapter(
            request=request,
            template_name="success_message.html",
            context={"message_html": success_html},
            templates=templates,
            url="/school/courses",
        )
    except ValidationError as ve:
        # Handle Pydantic validation errors specifically
        error_html = create_error_message(f"Validation error: {str(ve)}")
        return response_adapter(
            request=request,
            template_name="error_message.html",
            context={"message_html": error_html},
            templates=templates,
            status_code=400,
        )
    except Exception as e:
        # Generate error message
        error_html = create_error_message(str(e))

        # Return the error message
        return response_adapter(
            request=request,
            template_name="error_message.html",
            context={"message_html": error_html},
            templates=templates,
            status_code=400,
        )


@router.put("/courses/{course_id}", response_class=HTMLResponse)
async def update_course(
    request: Request,
    course_id: str,
    form_data: CourseCreate = Depends(
        lambda request: CourseCreate(
            code=request.form.get("code"),
            title=request.form.get("title"),
            active=request.form.get("active") == "true" or request.form.get("active") == "on",
        )
    ),
):
    """Update an existing course with Pydantic validation"""
    try:
        # Verify the course exists before updating
        existing_course = db_school.get("course", course_id)
        if existing_course.empty:
            raise HTTPException(status_code=404, detail="Course not found")

        # Create a validated Course model instance for the update
        updated_course = Course(id=course_id, **form_data.dict())

        # Update the course in the database using the model's serialization method
        db_school.update("course", updated_course.to_db_dict())

        # Generate success message
        success_html = create_success_message()

        # Return the success message
        return response_adapter(
            request=request,
            template_name="success_message.html",
            context={"message_html": success_html},
            templates=templates,
            url="/school/courses",
        )
    except ValidationError as ve:
        # Handle Pydantic validation errors specifically
        error_html = create_error_message(f"Validation error: {str(ve)}")
        return response_adapter(
            request=request,
            template_name="error_message.html",
            context={"message_html": error_html},
            templates=templates,
            status_code=400,
        )
    except HTTPException as he:
        # Pass through HTTP exceptions
        error_html = create_error_message(he.detail)
        return response_adapter(
            request=request,
            template_name="error_message.html",
            context={"message_html": error_html},
            templates=templates,
            status_code=he.status_code,
        )
    except Exception as e:
        # Generate error message
        error_html = create_error_message(str(e))

        # Return the error message
        return response_adapter(
            request=request,
            template_name="error_message.html",
            context={"message_html": error_html},
            templates=templates,
            status_code=400,
        )


@router.delete("/courses/{course_id}", response_class=HTMLResponse)
async def delete_course(request: Request, course_id: str):
    """Delete an existing course"""
    try:
        # Delete the course from the database
        db_school.delete("course", course_id)

        # Generate success message
        success_html = create_success_message()

        # Return the success message
        return response_adapter(
            request=request,
            template_name="success_message.html",
            context={"message_html": success_html},
            templates=templates,
            url="/school/courses",
        )
    except Exception as e:
        # Generate error message
        error_html = create_error_message(str(e))

        # Return the error message
        return response_adapter(
            request=request,
            template_name="error_message.html",
            context={"message_html": error_html},
            templates=templates,
            status_code=400,
        )

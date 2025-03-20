from dataclasses import asdict
from typing import Dict, List, Optional, Any
from uuid import UUID
import asyncio
import json

from fastapi import APIRouter, Depends, Request, Form, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder

# Try to import sse-starlette, fall back to a stub if not available
try:
    from sse_starlette.sse import EventSourceResponse
except ImportError:
    # Create a more robust fallback for EventSourceResponse until the package is installed
    from starlette.responses import StreamingResponse
    
    class EventSourceResponse(StreamingResponse):
        def __init__(self, content, status_code=200, headers=None, media_type="text/event-stream", **kwargs):
            self.ping_interval = kwargs.pop("ping_interval", 3)
            self.ping_message = kwargs.pop("ping_message", "")
            self.sep = kwargs.pop("sep", "\r\n")
            super().__init__(content=self.server_events(content), status_code=status_code, 
                            headers=headers, media_type=media_type)
        
        async def server_events(self, generator):
            async for event in generator:
                if isinstance(event, dict):
                    data = event.get("data", "")
                    event_type = event.get("event", "")
                    event_id = event.get("id", "")
                    retry = event.get("retry", "")
                    
                    message = []
                    if event_id:
                        message.append(f"id: {event_id}")
                    if retry:
                        message.append(f"retry: {retry}")
                    if event_type:
                        message.append(f"event: {event_type}")
                    if data:
                        if isinstance(data, str):
                            for line in data.split("\n"):
                                message.append(f"data: {line}")
                        else:
                            message.append(f"data: {data}")
                    
                    yield (self.sep.join(message) + self.sep + self.sep).encode("utf-8")
                elif isinstance(event, str):
                    yield f"data: {event}{self.sep}{self.sep}".encode("utf-8")
                else:
                    yield f"data: {event}{self.sep}{self.sep}".encode("utf-8")
                
                await asyncio.sleep(0.01)

import db.db_school as db_school
from db.models import Course
from datastar_py.responses import DatastarFastAPIResponse
from src.utils import serialize_data, json_dumps

router = APIRouter(prefix="/school", tags=["courses"])
templates = Jinja2Templates(directory="templates")

# Helper functions
def parse_filter_params(params: Dict[str, str]) -> Dict[str, str]:
    """Extract filter parameters from query params"""
    filters = {}
    for key, value in params.items():
        if key.startswith('filter_') and value:
            filter_name = key.replace('filter_', '')
            filters[filter_name] = value
    return filters

def filter_courses(courses: List[Dict[str, Any]], filters: Dict[str, str]) -> List[Dict[str, Any]]:
    """Apply filters to courses list"""
    filtered_courses = courses
    
    for key, value in filters.items():
        if key == 'code' and value:
            filtered_courses = [c for c in filtered_courses if value.lower() in c['code'].lower()]
        elif key == 'title' and value:
            filtered_courses = [c for c in filtered_courses if value.lower() in c['title'].lower()]
        elif key == 'active':
            is_active = value.lower() == 'true'
            filtered_courses = [c for c in filtered_courses if c['active'] == is_active]
            
    return filtered_courses

def sort_courses(courses: List[Dict[str, Any]], sort_by: Optional[str], sort_asc: bool) -> List[Dict[str, Any]]:
    """Sort courses by specified field"""
    if not sort_by:
        return courses
        
    reverse = not sort_asc
    return sorted(courses, key=lambda x: x.get(sort_by, ''), reverse=reverse)

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
    
    # Convert to JSON-compatible data
    json_compatible_courses = serialize_data(courses_dict)
    
    return templates.TemplateResponse(
        request=request, 
        name="school/courses.html",
        context={
            "courses": json_compatible_courses,
            "filters": {},
            "sort_by": None,
            "sort_asc": True
        }
    )

@router.get("/courses/new", response_class=HTMLResponse)
async def get_new_course_form(request: Request):
    """Get an empty course form for creating a new course"""
    return templates.TemplateResponse(
        request=request,
        name="school/course_form.html",
        context={"course": None}
    )

@router.get("/courses/data", response_class=HTMLResponse)
async def get_courses_data(
    request: Request,
    sort_by: Optional[str] = None,
    sort_asc: Optional[bool] = True
):
    """Get courses data for the table partial using server-side processing"""
    # Get filter parameters
    filters = parse_filter_params(dict(request.query_params))
    
    # Get all courses from the database
    db_courses = db_school.get_all("course")
    courses = [Course(**course.to_dict()) for _, course in db_courses.iterrows()]
    courses_dict = [asdict(course) for course in courses]
    
    # Convert to JSON-compatible data
    json_compatible_courses = serialize_data(courses_dict)
    
    # Apply filters
    filtered_courses = filter_courses(json_compatible_courses, filters)
    
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
            "sort_asc": sort_asc
        }
    )

@router.get("/courses/stream", response_class=EventSourceResponse)
async def stream_courses(request: Request):
    """Stream courses data using SSE for real-time updates"""
    async def event_generator():
        # Initial load
        try:
            async for event in send_courses_update():
                yield event
            
            # Keep connection alive with periodic updates
            while True:
                if await request.is_disconnected():
                    break
                    
                # Check for updates every 5 seconds
                await asyncio.sleep(5)
                
                async for event in send_courses_update():
                    yield event
        except Exception as e:
            # In case of an error, send an error event and close the connection
            yield {
                "event": "error",
                "id": "error",
                "data": str(e)
            }
            
    async def send_courses_update():
        try:
            # Get the latest courses data
            db_courses = db_school.get_all("course")
            courses = [Course(**course.to_dict()) for _, course in db_courses.iterrows()]
            courses_dict = [asdict(course) for course in courses]
            
            # Convert courses_dict to be JSON serializable
            json_compatible_courses = serialize_data(courses_dict)
            
            # Serialize to JSON string
            json_data = json_dumps({"courses": json_compatible_courses})
            
            # Return courses as a data event
            yield {
                "event": "courses_update",
                "id": "courses",
                "data": json_data
            }
        except Exception as e:
            # Log the error and yield an error event
            print(f"Error sending courses update: {str(e)}")
            yield {
                "event": "error",
                "id": "error",
                "data": str(e)
            }
        
    return EventSourceResponse(event_generator())
    
@router.get("/courses/{course_id}", response_class=HTMLResponse)
async def get_course(request: Request, course_id: str):
    """Get a single course for editing"""
    try:
        course_data = db_school.get("course", course_id)
        if course_data.empty:
            raise HTTPException(status_code=404, detail="Course not found")
            
        course = Course(**course_data.iloc[0].to_dict())
        course_dict = asdict(course)
        
        # Convert to JSON-compatible data
        json_compatible_course = serialize_data(course_dict)
        
        return templates.TemplateResponse(
            request=request,
            name="school/course_form.html",
            context={"course": json_compatible_course}
        )
    except Exception as e:
        error_msg = str(e)
        async def error_response(sse):
            yield create_error_message(sse, error_msg)
        return DatastarFastAPIResponse(error_response)

@router.post("/courses", response_class=HTMLResponse)
async def create_course(
    request: Request,
    code: str = Form(...),
    title: str = Form(...),
    active: bool = Form(False)
):
    """Create a new course"""
    try:
        # Create new course in the database
        new_course_data = db_school.create("course")
        
        # Update with form data
        course_id = str(new_course_data['id'])
        update_data = {
            "id": course_id,
            "code": code,
            "title": title,
            "active": active
        }
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
    active: bool = Form(False)
):
    """Update an existing course"""
    try:
        # Update course in the database
        update_data = {
            "id": course_id,
            "code": code,
            "title": title,
            "active": active
        }
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
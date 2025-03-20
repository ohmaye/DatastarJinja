from typing import Union

from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datastar_py.responses import DatastarFastAPIResponse
import asyncio
import datetime
from src.utils import is_datastar, serialize_data
from fastapi_tailwind import tailwind
from contextlib import asynccontextmanager
from menu_data import MENU_DATA
from src.school import router as school_router
import uuid
import os
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path

static_files = StaticFiles(directory = "static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # YAY, our tailwind get's compiled here! 😄
    process = tailwind.compile(
        static_files.directory + "/output.css",
        tailwind_stylesheet_path = static_files.directory + "/input.css"
    )

    yield # The code after this is called on shutdown.

    process.terminate() # We must terminate the compiler on shutdown to
    # prevent multiple compilers running in development mode or when watch is enabled.

app = FastAPI(
    # See the fastapi documentation for an explanation on lifespans: https://fastapi.tiangolo.com/advanced/events/
    lifespan = lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Add global context data to all templates
templates.env.globals["menu_data"] = MENU_DATA

# Add custom Jinja2 filters
def format_datetime(value):
    if isinstance(value, str):
        try:
            dt = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return value
        return dt.strftime("%Y-%m-%d %H:%M")
    elif isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return value

templates.env.filters["datetime"] = format_datetime

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes from other modules
app.include_router(school_router)

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/health", response_class=JSONResponse)
async def health_check():
    """
    Health check endpoint that also tests UUID serialization.
    This helps ensure the UUID serialization fix is working properly.
    """
    # Create a sample data structure with a UUID
    data = {
        "status": "ok",
        "version": "1.0.0",
        "uuid_test": uuid.uuid4(),
        "nested": {
            "uuid_field": uuid.uuid4()
        }
    }
    
    # Serialize the data to ensure UUIDs are handled correctly
    serialized_data = serialize_data(data)
    
    return JSONResponse(content=serialized_data)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(
        request=request, name="base.html", context={}
    )


@app.get("/items/{id}", response_class=HTMLResponse)
async def get_item(request: Request, id: str):
    return templates.TemplateResponse(
        request=request, name="item.html", context={"id": id}
    )

@app.get("/read_item/{id}")
def read_item(item_id: int, id:str):
    return {"item_id": id}


@app.get("/updates")
async def updates(request: Request):
    print("IS DATASTAR", is_datastar(request))
    async def tst(sse):
        yield sse.merge_fragments(["""<div id="hello">DID IT</div>"""])


    return DatastarFastAPIResponse(tst)
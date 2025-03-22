from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.utils import format_datetime, is_datastar
from fastapi_tailwind import tailwind
from contextlib import asynccontextmanager
from templates.layout.menu_data import NAV_DATA
from starlette.middleware.cors import CORSMiddleware


static_files = StaticFiles(directory="static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # YAY, our tailwind get's compiled here! 😄
    process = tailwind.compile(
        static_files.directory + "/output.css",
        tailwind_stylesheet_path=static_files.directory + "/input.css",
    )

    yield  # The code after this is called on shutdown.

    process.terminate()  # We must terminate the compiler on shutdown to
    # prevent multiple compilers running in development mode or when watch is enabled.


# app and templates shared across the project
app = FastAPI(
    # See the fastapi documentation for an explanation on lifespans: https://fastapi.tiangolo.com/advanced/events/
    lifespan=lifespan
)


templates = Jinja2Templates(directory="templates")

app.mount("/static", static_files, name="static")

# Add global context data to all templates
templates.env.globals["menu_data"] = NAV_DATA


# EO Not sure if this is needed
templates.env.filters["datetime"] = format_datetime


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

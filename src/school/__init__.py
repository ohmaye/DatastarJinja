from fastapi import APIRouter

from src.school.courses_routes import router as courses_router
# Import other school routers here as they are created

# Create a main router for the school module
router = APIRouter()

# Include all school routes
router.include_router(courses_router)
# Add other school routers here as they are created
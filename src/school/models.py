"""
Data models for the school module
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, ClassVar
from uuid import UUID
from datetime import datetime
import re


class Course(BaseModel):
    """
    Course data model with validation

    This model represents a course in the system with validation rules:
    - Course code must be 1-10 alphanumeric characters
    - Title must be 1-100 characters
    - ID must be a UUID string
    """

    id: str = Field(..., description="Unique course identifier")
    code: str = Field(..., min_length=1, max_length=10, description="Course code (e.g. CS101)")
    title: str = Field(..., min_length=1, max_length=100, description="Course title")
    active: bool = Field(False, description="Whether the course is active")

    # Validators
    @field_validator("code")
    def validate_code(cls, v):
        """Ensure code follows required format"""
        if not re.match(r"^[A-Za-z0-9\-_\.]{1,10}$", v):
            raise ValueError("Course code must be 1-10 alphanumeric characters")
        return v.upper()  # Normalize codes to uppercase

    @field_validator("id")
    def validate_id(cls, v):
        """Ensure ID is a valid UUID format (when not empty)"""
        if v and not re.match(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", v, re.I
        ):
            raise ValueError("ID must be a valid UUID format")
        return v

    # Add Pydantic config for additional behavior
    class Config:
        # Enable validation on assignment
        validate_assignment = True
        # Use arbitrary types (useful for more complex fields)
        arbitrary_types_allowed = True
        # Allow population by field name
        populate_by_name = True
        # Add schema title and description for API documentation
        title = "Course"
        description = "A course in the school system"
        # Add JSON schema examples
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "code": "CS101",
                "title": "Introduction to Computer Science",
                "active": True,
            }
        }

    # Helper methods for serialization/deserialization
    @classmethod
    def from_db_row(cls, row_dict: dict) -> "Course":
        """Create a Course instance from a database row dictionary"""
        return cls(**row_dict)

    def to_db_dict(self) -> dict:
        """Convert the course to a dictionary for database storage"""
        return self.model_dump(exclude_unset=True)

    def to_response_dict(self) -> dict:
        """Convert the course to a dictionary for API responses"""
        return self.model_dump()

    @property
    def display_name(self) -> str:
        """Get a formatted display name combining code and title"""
        return f"{self.code}: {self.title}"

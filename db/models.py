import uuid
from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Any, Dict, Optional, Type, TypeVar

T = TypeVar("T", bound="BaseModel")


@dataclass
class BaseModel:
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Creates an instance from a dictionary, ignoring extra keys"""
        # Get only the fields defined in the dataclass
        field_names = {f.name for f in fields(cls)}

        # Filter the input dict to only include valid fields
        filtered_data = {
            key: value for key, value in data.items() if key in field_names
        }

        return cls(**filtered_data)


@dataclass
class Course:
    id: uuid.UUID
    code: str
    title: str
    active: bool = field(default=False)


@dataclass
class Teacher:
    id: uuid.UUID
    name: str
    nameJP: str
    email: str
    note: str
    active: bool = field(default=False)


@dataclass
class Room:
    id: uuid.UUID
    name: str
    type: str
    capacity: int
    active: bool = field(default=False)


@dataclass
class Timeslot:
    id: uuid.UUID
    weekday: str
    start_time: str
    end_time: str
    active: bool = field(default=False)


# SPIN MODELS
@dataclass
class SpinClass:
    id: uuid.UUID
    title: str
    course_code: str
    timeslot: str
    teacher_name: str
    room_name: str
    for_program: str


@dataclass
class Student(BaseModel):
    email: str
    firstName: str
    lastName: str
    level: str
    program: str
    created_at: datetime = field(default_factory=datetime.now)
    active: bool = field(default=False)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Student_Selection(BaseModel):
    student_id: uuid.UUID
    preference_code: str
    course_code: str
    assigned: bool = field(default=False)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Assignment(BaseModel):
    student_id: uuid.UUID
    spin_class_id: uuid.UUID
    uploaded: bool = field(default=False)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Survey_Level:
    id: uuid.UUID
    level: str


@dataclass
class Survey_Group:
    id: uuid.UUID
    course_group: str
    course_code: str
    course_title: str
    active: bool = field(default=False)


@dataclass
class Survey_Table:
    id: uuid.UUID
    name: str
    description: str
    option_codes: str
    courses_group: str


@dataclass
class Survey_Image:
    id: uuid.UUID
    filename: str
    content: Optional[bytes]


@dataclass
class Survey:
    id: uuid.UUID
    title: str
    introduction: str
    explanation: str
    intensive_chart: str  # UUID for Secodary Key image
    intensive_table_1: str  # UUID for Secodary Key survey_table
    intensive_table_2: str  # UUID for Secodary Key survey_table
    general_chart: str  # UUID for Secodary Key image
    general_table: str  # UUID for Secodary Key survey_table


@dataclass
class Survey_Config:
    id: str
    current_survey: str  # UUID
    active: bool = field(default=False)

"""
Data models for the school module
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from uuid import UUID


@dataclass
class Course:
    """Course data model"""
    id: str
    code: str
    title: str
    active: bool = False
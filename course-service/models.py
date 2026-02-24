from pydantic import BaseModel
from typing import Optional

class Course(BaseModel):
    id: int
    name: str
    description: str
    duration: int

class CourseCreate(BaseModel):
    name: str
    description: str
    duration: int

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
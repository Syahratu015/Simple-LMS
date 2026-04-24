from ninja import Schema
from typing import Optional


class CourseIn(Schema):
    title: str
    description: str


class CourseOut(Schema):
    id: int
    title: str
    description: str
    instructor_id: int
    instructor_name: Optional[str] = None
    total_lessons: Optional[int] = 0

    @staticmethod
    def resolve_instructor_name(obj):
        return obj.instructor.username
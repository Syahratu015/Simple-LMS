from ninja import Router
from typing import List
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import Course, Lesson
from .schemas import CourseIn, CourseOut
from core.auth import JWTAuth

router = Router()


# ======================
# PUBLIC
# ======================

@router.get("/", response=List[CourseOut])
def list_courses(request):
    courses = Course.objects.select_related(
        "instructor",
        "category"
    ).annotate(
        total_lessons=Count("lessons")
    )
    return courses


@router.get("/{course_id}", response=CourseOut)
def course_detail(request, course_id: int):
    course = get_object_or_404(
        Course.objects.select_related("instructor", "category"),
        id=course_id
    )
    return course


# ======================
# LESSON API
# ======================

@router.get("/{course_id}/lessons")
def course_lessons(request, course_id: int):
    lessons = Lesson.objects.filter(course_id=course_id).order_by("order")

    return [
        {
            "id": l.id,
            "title": l.title,
            "order": l.order
        }
        for l in lessons
    ]


# ======================
# PROTECTED (JWT)
# ======================

@router.post("/", auth=JWTAuth())
def create_course(request, payload: CourseIn):

    user = request.auth

    if user.role != "instructor":
        return {"error": "Only instructor can create course"}

    course = Course.objects.create(
        title=payload.title,
        description=payload.description,
        instructor=user
    )

    return {
        "message": "Course created",
        "id": course.id
    }


@router.patch("/{course_id}", auth=JWTAuth())
def update_course(request, course_id: int, payload: CourseIn):

    user = request.auth

    course = get_object_or_404(Course, id=course_id)

    if course.instructor != user:
        return {"error": "Not owner"}

    course.title = payload.title
    course.description = payload.description
    course.save()

    return {"message": "updated"}


@router.delete("/{course_id}", auth=JWTAuth())
def delete_course(request, course_id: int):

    user = request.auth

    if user.role != "admin":
        return {"error": "Only admin can delete"}

    course = get_object_or_404(Course, id=course_id)
    course.delete()

    return {"message": "deleted"}
from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django_ratelimit.decorators import ratelimit

from .models import Course
from .auth import JWTAuth, require_role
from .mongo_utils import log_activity, log_learning_analytics

# Import Celery Tasks
from .tasks import (
    send_enrollment_email,
    generate_certificate,
    update_course_statistics,
    export_course_report,
)

router = Router()


# ========================
# SCHEMAS
# ========================
class CourseOutSchema(Schema):
    id: int
    title: str
    description: str


class CourseCreateSchema(Schema):
    title: str
    description: str


class CourseUpdateSchema(Schema):
    title: str = None
    description: str = None


class EnrollmentOutSchema(Schema):
    message: str
    course_id: int
    student_id: int


# ========================
# LIST COURSES
# ========================
@router.get("/")
@ratelimit(key="ip", rate="60/m", block=True)
def list_courses(
    request,
    search: str = None,
    category_id: int = None,
    sort: str = None,
):
    courses = Course.objects.all()

    if search:
        courses = courses.filter(title__icontains=search)

    if category_id:
        courses = courses.filter(category_id=category_id)

    if sort == "title":
        courses = courses.order_by("title")
    elif sort == "-title":
        courses = courses.order_by("-title")
    elif sort == "newest":
        courses = courses.order_by("-id")

    return {
        "data": list(
            courses.values(
                "id",
                "title",
                "description",
            )
        )
    }


# ========================
# DETAIL COURSE
# ========================
@router.get("/{course_id}")
@ratelimit(key="ip", rate="60/m", block=True)
def get_course(request, course_id: int):
    cache_key = f"course_detail_{course_id}"

    cached = cache.get(cache_key)
    if cached:
        return {
            "source": "redis_cache",
            "data": cached,
        }

    course = (
        Course.objects.filter(id=course_id)
        .values(
            "id",
            "title",
            "description",
        )
        .first()
    )

    if not course:
        return {"error": "Course not found"}

    cache.set(cache_key, course, timeout=300)

    return {
        "source": "database",
        "data": course,
    }


# ========================
# CREATE COURSE
# ========================
@router.post("/", auth=JWTAuth())
@require_role(["instructor"])
def create_course(request, data: CourseCreateSchema):
    user = request.auth

    course = Course.objects.create(
        title=data.title,
        description=data.description,
        instructor=user,
    )

    log_activity(
        user_id=user.id,
        action="CREATE_COURSE",
        detail=f"Course '{course.title}' created",
    )

    log_learning_analytics(
        user_id=user.id,
        course_id=course.id,
        event_type="COURSE_CREATED",
        progress=0,
    )

    cache.clear()

    # Jalankan Celery
    update_course_statistics.delay()

    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
    }


# ========================
# UPDATE COURSE
# ========================
@router.patch("/{course_id}", auth=JWTAuth())
@require_role(["instructor"])
def update_course(request, course_id: int, data: CourseUpdateSchema):
    user = request.auth
    course = get_object_or_404(Course, id=course_id)

    if course.instructor != user:
        return {"error": "Not your course"}

    if data.title is not None:
        course.title = data.title

    if data.description is not None:
        course.description = data.description

    course.save()

    log_activity(
        user_id=user.id,
        action="UPDATE_COURSE",
        detail=f"Course ID {course_id} updated",
    )

    cache.clear()
    cache.delete(f"course_detail_{course_id}")

    # Jalankan Celery
    update_course_statistics.delay()

    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
    }


# ========================
# DELETE COURSE
# ========================
@router.delete("/{course_id}", auth=JWTAuth())
@require_role(["admin"])
def delete_course(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)

    log_activity(
        user_id=request.auth.id,
        action="DELETE_COURSE",
        detail=f"Course ID {course_id} deleted",
    )

    course.delete()

    cache.clear()
    cache.delete(f"course_detail_{course_id}")

    return {
        "message": "Deleted successfully"
    }


# ========================
# EXPORT REPORT
# ========================
@router.post("/{course_id}/export", auth=JWTAuth())
@require_role(["instructor", "admin"])
def export_report(request, course_id: int):
    export_course_report.delay(course_id)

    return {
        "message": "Export report task submitted"
    }


# ========================
# ENROLL COURSE
# ========================
@router.post(
    "/{course_id}/enroll",
    auth=JWTAuth(),
    response=EnrollmentOutSchema,
)
@require_role(["student"])
def enroll_course(request, course_id: int):
    user = request.auth
    course = get_object_or_404(Course, id=course_id)

    if hasattr(course, "students"):
        if course.students.filter(id=user.id).exists():
            return {
                "message": "You are already enrolled in this course",
                "course_id": course.id,
                "student_id": user.id,
            }

        course.students.add(user)

    log_activity(
        user_id=user.id,
        action="ENROLL_COURSE",
        detail=f"Student enrolled in Course ID {course_id}",
    )

    log_learning_analytics(
        user_id=user.id,
        course_id=course.id,
        event_type="COURSE_ENROLLED",
        progress=0,
    )

    # Jalankan Celery
    send_enrollment_email.delay(
        user.email,
        course.title,
    )

    generate_certificate.delay(
        user.id,
        course.id,
    )

    return {
        "message": "Successfully enrolled",
        "course_id": course.id,
        "student_id": user.id,
    }
from ninja import Router
from django.shortcuts import get_object_or_404
from courses.models import Enrollment
from courses.models import Course
from core.auth import JWTAuth

router = Router()


# =========================
# ENROLL COURSE
# =========================
@router.post("/", auth=JWTAuth())
def enroll_course(request, course_id: int):
    user = request.auth

    if not user:
        return {"error": "Unauthorized"}

    course = get_object_or_404(Course, id=course_id)

    enrollment, created = Enrollment.objects.get_or_create(
        student=user,
        course=course
    )

    if not created:
        return {"message": "Already enrolled"}

    return {
        "message": "Enrolled successfully",
        "course": course.title
    }


# =========================
# MY COURSES (OPTIMIZED)
# =========================
@router.get("/my", auth=JWTAuth())
def my_courses(request):
    user = request.auth

    if not user:
        return {"error": "Unauthorized"}

    # ✅ pakai custom queryset (WAJIB untuk nilai)
    enrollments = Enrollment.objects.for_student_dashboard().filter(
        student=user
    )

    return [
        {
            "course": e.course.title,
            "progress": sum(
                1 for p in e.progress_set.all() if p.completed
            ),
            "total_lessons": e.progress_set.count()
        }
        for e in enrollments
    ]
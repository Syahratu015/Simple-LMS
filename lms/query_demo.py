from django.db import connection, reset_queries
from .models import Course, Enrollment


def show_queries():
    for query in connection.queries:
        print(query['sql'])


# =========================
# N+1 Problem
# =========================

def n_plus_one_problem():
    reset_queries()

    courses = Course.objects.all()

    for course in courses:
        print(course.instructor.username)

    print("Total Queries:", len(connection.queries))


# =========================
# Optimized Query
# =========================

def optimized_query():
    reset_queries()

    courses = Course.objects.select_related('instructor')

    for course in courses:
        print(course.instructor.username)

    print("Total Queries:", len(connection.queries))


# =========================
# Enrollment Dashboard
# =========================

def student_dashboard():
    reset_queries()

    enrollments = Enrollment.objects.for_student_dashboard()

    for enroll in enrollments:
        print(enroll.student.username, enroll.course.title)

    print("Total Queries:", len(connection.queries))
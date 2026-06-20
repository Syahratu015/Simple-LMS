from celery import shared_task


@shared_task
def send_enrollment_email(email, course_title):
    print(
        f"Email sent to {email} for course {course_title}"
    )
    return True


@shared_task
def generate_certificate(user_id, course_id):
    print(
        f"Generate certificate for user {user_id}"
    )
    return True


@shared_task
def update_course_statistics():
    print(
        "Updating course statistics..."
    )
    return True


@shared_task
def export_course_report(course_id):
    print(
        f"Exporting report for course {course_id}"
    )
    return True
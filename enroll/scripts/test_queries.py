from courses.models import Course

# ❌ N+1
courses = Course.objects.all()
for c in courses:
    print(c.instructor.username)

# ✅ optimized
courses = Course.objects.select_related("instructor")
for c in courses:
    print(c.instructor.username)
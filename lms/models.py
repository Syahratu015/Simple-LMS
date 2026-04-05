from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# ========================
# User Model
# ========================

class User(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )

    def __str__(self):
        return self.username


# ========================
# Category Model
# ========================

class Category(models.Model):

    name = models.CharField(max_length=255)

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    def __str__(self):
        return self.name


# ========================
# Custom Queryset Course
# ========================

class CourseQuerySet(models.QuerySet):

    def for_listing(self):
        return self.select_related(
            'instructor',
            'category'
        ).prefetch_related(
            'lessons'
        )


# ========================
# Course Model
# ========================

class Course(models.Model):

    title = models.CharField(max_length=255)

    description = models.TextField()

    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='courses',
        limit_choices_to={'role': 'instructor'}
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='courses'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    objects = CourseQuerySet.as_manager()

    def __str__(self):
        return self.title


# ========================
# Lesson Model
# ========================

class Lesson(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons'
    )

    title = models.CharField(max_length=255)

    content = models.TextField()

    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order')

    def __str__(self):
        return self.title


# ========================
# Enrollment Queryset
# ========================

class EnrollmentQuerySet(models.QuerySet):

    def for_student_dashboard(self):
        return self.select_related(
            'student',
            'course'
        ).prefetch_related(
            'progress',
            'course__lessons'
        )


# ========================
# Enrollment Model
# ========================

class Enrollment(models.Model):

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'}
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    enrolled_at = models.DateTimeField(auto_now_add=True)

    objects = EnrollmentQuerySet.as_manager()

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} - {self.course}"


# ========================
# Progress Model
# ========================

class Progress(models.Model):

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='progress'
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE
    )

    completed = models.BooleanField(default=False)

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('enrollment', 'lesson')

    def mark_completed(self):
        self.completed = True
        self.completed_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.enrollment} - {self.lesson}"
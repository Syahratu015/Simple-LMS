from django.contrib import admin
from .models import User, Category, Course, Lesson, Enrollment, Progress


# ========================
# Lesson Inline
# ========================

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    ordering = ('order',)


# ========================
# Course Admin
# ========================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'instructor',
        'category',
        'created_at'
    )

    ordering = (
        '-created_at',
    )

    search_fields = (
        'title',
        'description',
        'instructor__username'
    )

    list_filter = (
        'category',
        'instructor'
    )

    date_hierarchy = 'created_at'

    inlines = [LessonInline]

    # Query Optimization
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'instructor',
            'category'
        )


# ========================
# Category Admin
# ========================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'parent'
    )

    ordering = (
        'name',
    )

    search_fields = (
        'name',
    )

    list_filter = (
        'parent',
    )


# ========================
# Lesson Admin
# ========================

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'course',
        'order'
    )

    ordering = (
        'course',
        'order'
    )

    search_fields = (
        'title',
    )

    list_filter = (
        'course',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'course'
        )


# ========================
# Enrollment Admin
# ========================

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'course',
        'enrolled_at'
    )

    ordering = (
        '-enrolled_at',
    )

    search_fields = (
        'student__username',
        'course__title'
    )

    list_filter = (
        'course',
        'enrolled_at'
    )

    date_hierarchy = 'enrolled_at'

    # Query Optimization
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student',
            'course'
        )


# ========================
# Progress Admin
# ========================

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):

    list_display = (
        'enrollment',
        'lesson',
        'completed',
        'completed_at'
    )

    ordering = (
        '-completed_at',
    )

    list_filter = (
        'completed',
    )

    search_fields = (
        'lesson__title',
        'enrollment__student__username'
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'enrollment',
            'lesson'
        )


# ========================
# User Admin
# ========================

@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        'username',
        'email',
        'role',
        'is_active'
    )

    ordering = (
        'username',
    )

    list_filter = (
        'role',
        'is_active'
    )

    search_fields = (
        'username',
        'email'
    )
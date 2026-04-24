from django.contrib import admin
from django.db.models import Count
from .models import Course, Lesson, Category, Enrollment, Progress


# ========================
# Lesson Inline
# ========================

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    ordering = ('order',)


# ========================
# Progress Inline
# ========================

class ProgressInline(admin.TabularInline):
    model = Progress
    extra = 0


# ========================
# Course Admin
# ========================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    def total_lessons(self, obj):
        return obj.total_lessons
    total_lessons.short_description = "Lessons"

    list_display = (
        "title",
        "instructor",
        "category",
        "total_lessons",
        "created_at"
    )

    search_fields = (
        "title",
        "description",
        "instructor__username"
    )

    list_filter = (
        "category",
        "instructor"
    )

    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    inlines = [LessonInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "instructor",
            "category"
        ).annotate(
            total_lessons=Count("lessons")
        )


# ========================
# Category Admin
# ========================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    def full_path(self, obj):
        if obj.parent:
            return f"{obj.parent.name} → {obj.name}"
        return obj.name
    full_path.short_description = "Category"

    list_display = ("full_path", "parent")
    search_fields = ("name",)
    list_filter = ("parent",)
    ordering = ("name",)


# ========================
# Lesson Admin
# ========================

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):

    list_display = ("title", "course", "order")

    search_fields = ("title",)

    list_filter = ("course",)

    ordering = ("course", "order")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("course")


# ========================
# Enrollment Admin
# ========================

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):

    def progress_percentage(self, obj):
        total = obj.progress_set.count()
        if total == 0:
            return "0%"
        completed = obj.progress_set.filter(completed=True).count()
        return f"{int((completed / total) * 100)}%"
    progress_percentage.short_description = "Progress"

    list_display = (
        "student",
        "course",
        "progress_percentage",
        "enrolled_at"
    )

    search_fields = (
        "student__username",
        "course__title"
    )

    list_filter = (
        "course",
        "enrolled_at"
    )

    ordering = ("-enrolled_at",)
    date_hierarchy = "enrolled_at"

    inlines = [ProgressInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "student",
            "course"
        ).prefetch_related(
            "progress_set__lesson"
        )


# ========================
# Progress Admin
# ========================

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):

    list_display = (
        "enrollment",
        "lesson",
        "completed",
        "completed_at"
    )

    search_fields = (
        "lesson__title",
        "enrollment__student__username"
    )

    list_filter = ("completed",)

    ordering = ("-completed_at",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "enrollment",
            "lesson"
        )
from django.contrib import admin
from .models import Course

# Register your models here.


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "creator", "language", "base_language", "is_public", "created_at")
    list_filter = ("is_public", "language", "base_language", "created_at")
    search_fields = ("name", "creator__username")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {
            "fields": ("name", "creator", "is_public")
        }),
        ("Språkinställningar", {
            "fields": ("language", "base_language")
        }),
        ("Medlemmar", {
            "fields": ("members",)
        }),
    )

    readonly_fields = ("created_at",)

    autocomplete_fields = ("creator", "members")
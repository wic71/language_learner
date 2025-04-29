# core/templatetags/progress_tags.py

from django import template

from core.models import UserModule

register = template.Library()


@register.filter
def get_progress(user, course):
    total_modules = course.modules.count()
    if total_modules == 0:
        return 0
    completed = UserModule.objects.filter(
        user=user, module__course=course, completed_at__isnull=False
    ).count()
    return int((completed / total_modules) * 100)

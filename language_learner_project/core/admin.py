from adminsortable2.admin import (
    SortableAdminBase,
    SortableAdminMixin,
    SortableInlineAdminMixin,
)
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import (
    UserAdmin as BaseUserAdmin,
    UserAdmin as DefaultUserAdmin,
)
from django.contrib.auth.models import User as AuthUser
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Course, Module, Sentence, UserModule, Word

User = get_user_model()


# --- Inline för UserModule ---
class UserModuleInline(admin.TabularInline):
    model = UserModule
    extra = 0
    readonly_fields = ("module", "completed")
    can_delete = False


# --- Inline för Moduler i Kurs ---
class ModuleInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Module
    extra = 0
    fields = ("order", "title", "description")
    ordering = ("order",)
    show_change_link = True


# --- Inline för Meningar i Modul ---
class SentenceInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Sentence
    extra = 0
    fields = ("order", "text", "translation", "audio")
    ordering = ("order",)


# --- Inline för Ord i Modul ---
class WordInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Word
    extra = 0
    fields = ("text", "translation", "example_sentence", "image", "audio")
    autocomplete_fields = ("example_sentence",)


# --- Kursadmin ---
@admin.register(Course)
class CourseAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = (
        "name",
        "creator",
        "language",
        "base_language",
        "is_public",
        "created_at",
    )
    list_filter = ("language", "base_language", "is_public")
    search_fields = ("name", "creator__username")
    ordering = ("-created_at",)
    filter_horizontal = ("members",)
    inlines = [ModuleInline]
    actions = ["duplicate_courses"]
    readonly_fields = ("created_at",)

    fieldsets = (
        (None, {"fields": ("name", "description", "creator", "is_public")}),
        ("Språkinställningar", {"fields": ("language", "base_language")}),
        ("Medlemmar", {"fields": ("members",)}),
    )

    @admin.action(description="Duplicera valda kurser")
    def duplicate_courses(self, request, queryset):
        for course in queryset:
            new_course = Course.objects.create(
                name=f"{course.name} (Kopia)",
                description=course.description,
                language=course.language,
                base_language=course.base_language,
                is_public=False,
                creator=course.creator,
            )
            new_course.members.set(course.members.all())
            for module in course.modules.all():
                Module.objects.create(
                    course=new_course,
                    title=module.title,
                    description=module.description,
                    text=module.text,
                    order=module.order,
                )


# --- Moduladmin ---
@admin.register(Module)
class ModuleAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("title", "course", "order", "get_usermodule_count")
    ordering = ("course", "order")
    search_fields = ("title",)
    autocomplete_fields = ("course",)
    inlines = [SentenceInline, WordInline]

    def get_usermodule_count(self, obj):
        return obj.usermodules.count()

    get_usermodule_count.short_description = "Antal användare"


# --- Meningadmin ---
@admin.register(Sentence)
class SentenceAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("text", "module", "order")
    ordering = ("module", "order")
    search_fields = ("text", "module__title")
    autocomplete_fields = ("module",)


# --- Ordadmin ---
@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = (
        "text",
        "module",
        "translation",
        "example_sentence",
        "audio_player",
        "image_preview",
    )
    ordering = ("module", "text")
    autocomplete_fields = ("module", "example_sentence")
    readonly_fields = ("audio_player", "image_preview")

    def audio_player(self, obj):
        if obj.audio:
            return mark_safe(f'<audio controls src="{obj.audio.url}"></audio>')
        return "-"

    audio_player.short_description = "Ljud"

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')
        return "-"

    image_preview.short_description = "Bild"


# Avregistrera den inbyggda User
admin.site.unregister(AuthUser)


# --- Användaradmin ---
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserModuleInline]
    list_display = ("username", "email", "get_joined_courses", "is_staff", "is_active")
    search_fields = ("username", "email")
    ordering = ("date_joined",)

    def get_joined_courses(self, obj):
        return ", ".join([course.name for course in obj.joined_courses.all()])

    get_joined_courses.short_description = "Kurser"


from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

from .models import Course, Module, UserModule


class LanguageLearnerAdminSite(AdminSite):
    site_header = "Language Learner Admin"
    site_title = "Language Learner"
    index_title = "Översikt"

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        # Sortera app-listan om du vill
        return app_list

    def each_context(self, request):
        context = super().each_context(request)

        context['latest_courses'] = Course.objects.order_by('-created_at')[:5]
        context['latest_modules'] = Module.objects.order_by('-created_at')[:5]
        context['latest_students'] = User.objects.order_by('-date_joined')[:5]

        return context

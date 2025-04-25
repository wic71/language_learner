from django.db import models
from django.conf import settings
from django.db import models
from core.languages import LANGUAGE_CHOICES

# Create your models here.
class Course(models.Model):
    name = models.CharField(max_length=255, verbose_name="Kursnamn (på basspråket)")
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, verbose_name="Språk att lära sig")
    base_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, verbose_name="Basspråk")
    is_public = models.BooleanField(default=False, verbose_name="Publik kurs")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_courses")
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="joined_courses", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kurser"

    def __str__(self):
        return f"{self.name} ({self.get_language_display()})"
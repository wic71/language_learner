from django import forms
from .models import Course
from .languages import LANGUAGE_CHOICES

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "language", "base_language", "is_public"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "language": forms.Select(choices=LANGUAGE_CHOICES),
            "base_language": forms.Select(choices=LANGUAGE_CHOICES),
        }
        labels = {
            "name": "Kursnamn",
            "language": "Språk att lära sig",
            "base_language": "Basspråk",
            "is_public": "Publik",
        }

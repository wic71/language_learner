from django import forms

from .languages import LANGUAGE_CHOICES
from .models import Course, Module, Sentence


class SentenceForm(forms.ModelForm):
    class Meta:
        model = Sentence
        fields = ['text', 'translation']


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "description", "language", "base_language", "is_public"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-textarea"}),
            "language": forms.Select(choices=LANGUAGE_CHOICES),
            "base_language": forms.Select(choices=LANGUAGE_CHOICES),
        }
        labels = {
            "name": "Kursnamn",
            "description": "Beskrivning",
            "language": "Språk att lära sig",
            "base_language": "Basspråk",
            "is_public": "Publik",
        }


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ["title", "description", "text", "excluded_words"]

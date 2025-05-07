import bleach
from django import forms

from .languages import LANGUAGE_CHOICES
from .models import Course, Module, Sentence, Exercise

# Tillåtna HTML-taggar – andra tas bort för att undvika XSS
ALLOWED_TAGS = ['p', 'br', 'ul', 'ol', 'li', 'b', 'i']


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
    """
    Formulär för att skapa och redigera en modul. Rensar HTML i textfält enligt whitelist.
    """

    class Meta:
        model = Module
        fields = ['title', 'description', 'text', 'excluded_words']

    def clean_description(self):
        """
        Rensar beskrivningen från otillåten HTML.
        """
        desc = self.cleaned_data.get('description', '')
        return bleach.clean(desc, tags=ALLOWED_TAGS)

    def clean_text(self):
        """
        Rensar textfältet från otillåten HTML.
        """
        text = self.cleaned_data.get('text', '')
        return bleach.clean(text, tags=ALLOWED_TAGS)



class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'description', 'considerations']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'considerations': forms.Textarea(attrs={'rows': 3}),
        }
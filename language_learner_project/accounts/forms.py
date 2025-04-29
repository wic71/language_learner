from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Anpassat registreringsformulär som bygger på Django UserCreationForm.
    """

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lägg till Tailwind-klasser
        for field in self.fields.values():
            field.widget.attrs.update(
                {
                    "class": "w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                }
            )

from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required

from core.models import Course
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = "registration/login.html"

class CustomPasswordResetView(PasswordResetView):
    template_name = "registration/password_reset.html"

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"

# Create your views here.

def signup_view(request):
    """
    Hanterar användarregistrering.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Logga in användaren direkt
            return redirect("home")  # Justera till rätt URL för hem
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})



@login_required
def profile_view(request):
    created_courses = Course.objects.filter(creator=request.user)
    return render(request, "accounts/profile.html", {"created_courses": created_courses})


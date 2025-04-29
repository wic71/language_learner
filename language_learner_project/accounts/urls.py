from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    CustomLoginView,
    CustomPasswordResetCompleteView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetDoneView,
    CustomPasswordResetView,
    profile_view,
    signup_view,
)

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("profile/", profile_view, name="profile"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # Lösenordsåterställning
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "password_reset/done/",
        CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]

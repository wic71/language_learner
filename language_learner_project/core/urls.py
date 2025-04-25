from django.contrib import admin
from django.urls import path, include
from . import views
from .views import course_detail, edit_course, create_course

urlpatterns = [
    path('', views.home, name='home'),
    path('partial/time/', views.time_partial, name='time_partial'),
    #path("accounts/", include("django.contrib.auth.urls")),  # login/logout/reset osv.
    path("accounts/", include("accounts.urls")),  # egna views, t.ex. signup
    path("courses/<int:pk>/", course_detail, name="course_detail"),
    path("courses/<int:pk>/edit/", edit_course, name="course_edit"),
    path("courses/new/", create_course, name="course_create"),

]
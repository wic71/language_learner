from datetime import datetime
from .models import Course
from django.contrib.auth.decorators import login_required
from .forms import CourseForm
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
def home(request):
    return render(request, "home.html")

def time_partial(request):
    return render(request, "partials/time.html", {"now": datetime.now()})


@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    return render(request, "courses/course_detail.html", {"course": course})


@login_required
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk, creator=request.user)

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = CourseForm(instance=course)

    return render(request, "courses/course_edit.html", {"form": form, "course": course})


@login_required
def create_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.creator = request.user
            course.save()
            course.members.add(request.user)  # Gör skaparen till medlem
            return redirect("profile")
    else:
        form = CourseForm()

    return render(request, "courses/course_create.html", {"form": form})


@login_required
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk, creator=request.user)

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = CourseForm(instance=course)

    return render(request, "courses/course_edit.html", {"form": form, "course": course})
from django.contrib import admin
from django.urls import include, path

from core.views import sentence_delete_audio, sentence_upload_audio

from . import views
from .views import *

urlpatterns = [
    path('', views.home, name='home'),
    path('partial/time/', views.time_partial, name='time_partial'),
    # path("accounts/", include("django.contrib.auth.urls")),  # login/logout/reset osv.
    path("accounts/", include("accounts.urls")),  # egna views, t.ex. signup
    path("courses/<int:pk>/", course_detail, name="course_detail"),
    path("courses/new/", create_course, name="course_create"),
    path("courses/htmx/new/", create_course_modal, name="course_modal"),
    path("courses/htmx/submit/", create_course_submit, name="course_submit"),
    path("courses/explore/", views.explore_courses, name="explore_courses"),
    path("courses/<int:pk>/join/", views.join_course, name="join_course"),
    path("courses/<int:pk>/edit/", edit_course, name="edit_course"),
    path("courses/<int:pk>/modules/", edit_course_modules, name="edit_course_modules"),
    path('courses/<int:pk>/modules/new/', module_create, name='module_create'),
    path('modules/<int:pk>/edit/', module_edit, name='module_edit'),
    path('courses/<int:pk>/modules/reorder/', module_reorder, name='module_reorder'),
    path('modules/<int:pk>/delete/', views.module_delete, name='module_delete'),
    path(
        "modules/<int:pk>/generate_sentences/",
        views.generate_sentences,
        name="generate_sentences",
    ),
    path("sentences/<int:pk>/edit/", views.sentence_edit, name="sentence_edit"),
    path(
        'modules/<int:pk>/regenerate_sentences/',
        regenerate_sentences,
        name='regenerate_sentences',
    ),
    path(
        'sentences/<int:pk>/inline_edit/',
        sentence_inline_edit,
        name='sentence_inline_edit',
    ),
    path(
        'sentences/<int:pk>/upload_audio/',
        sentence_upload_audio,
        name='sentence_upload_audio',
    ),
    path(
        'sentences/<int:pk>/delete_audio/',
        sentence_delete_audio,
        name='sentence_delete_audio',
    ),
    # Word (Ord) API
    path(
        'words/<int:pk>/edit_translation/',
        edit_word_translation,
        name='edit_word_translation',
    ),
    path('words/<int:pk>/upload_image/', upload_word_image, name='upload_word_image'),
    path('words/<int:pk>/upload_audio/', upload_word_audio, name='upload_word_audio'),
    path(
        "sentences/<int:pk>/delete_audio/",
        views.sentence_delete_audio,
        name="sentence_delete_audio",
    ),
    path(
        "words/<int:pk>/delete_audio/",
        views.word_delete_audio,
        name="word_delete_audio",
    ),
    path('rosetta/', include('rosetta.urls')),
    path('modules/<int:pk>/', module_detail, name='module_detail'),
    path('modules/<int:pk>/complete/', complete_module, name='complete_module'),
    path('modules/<int:pk>/start/', start_module, name='start_module'),


    path('exercises/create/<int:module_id>/', views.create_exercise, name='create_exercise'),
    path('exercises/edit/<int:pk>/', views.edit_exercise, name='edit_exercise'),
    path('exercises/delete/<int:pk>/', views.delete_exercise, name='delete_exercise'),
]

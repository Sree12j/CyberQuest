from django.urls import path

from . import views

urlpatterns = [
    path("", views.learning_paths, name="learning_paths"),
    path("<slug:slug>/", views.learning_path_detail, name="learning_path_detail"),
    path(
        "<slug:path_slug>/<slug:lesson_slug>/",
        views.lesson_detail,
        name="lesson_detail",
    ),
    path(
        "<slug:path_slug>/<slug:lesson_slug>/answer/",
        views.lesson_question_answer,
        name="lesson_question_answer",
    ),
    path(
        "<slug:path_slug>/<slug:lesson_slug>/complete/",
        views.lesson_complete,
        name="lesson_complete",
    ),
]

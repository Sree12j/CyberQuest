from pathlib import Path
from urllib.parse import urlparse

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import LearningPath, Lesson, LessonProgress, LessonQuestion, LessonResponse

# Presentation-only mapping. Icons and colours are not model fields, so the
# database schema stays unchanged for learning paths.
PATH_VISUALS = {
    "phishing-detective": ("mail-warning", "green"),
    "password-guardian": ("key-round", "cyan"),
    "privacy-protector": ("eye-off", "purple"),
    "network-navigator": ("network", "blue"),
    "mobile-defender": ("smartphone", "orange"),
    "data-defender": ("database", "pink"),
}


def published_paths():
    """Return published paths with an accurate published-lesson count."""
    return (
        LearningPath.objects.filter(is_published=True)
        .annotate(
            lesson_count=Count(
                "lessons",
                filter=Q(lessons__is_published=True),
                distinct=True,
            )
        )
        .order_by("title")
    )


def add_path_visuals(paths):
    """Attach icon/colour names used by the CyberQuest cards."""
    for path in paths:
        icon, tone = PATH_VISUALS.get(path.slug, ("route", "green"))
        path.icon = icon
        path.tone = tone
    return paths


def learning_paths(request):
    """Show all published learning paths from the database."""
    paths = add_path_visuals(list(published_paths()))
    return render(
        request,
        "learning/paths_placeholder.html",
        {"learning_paths": paths},
    )


def learning_path_detail(request, slug):
    """Show one published path and its published lessons in lesson order."""
    published_lessons = Prefetch(
        "lessons",
        queryset=Lesson.objects.filter(is_published=True).order_by("order", "title"),
        to_attr="visible_lessons",
    )

    path = get_object_or_404(
        LearningPath.objects.filter(is_published=True)
        .prefetch_related(published_lessons)
        .annotate(
            published_lesson_count=Count(
                "lessons",
                filter=Q(lessons__is_published=True),
                distinct=True,
            )
        ),
        slug=slug,
    )

    add_path_visuals([path])
    return render(
        request,
        "learning/path_detail.html",
        {
            "path": path,
            "lessons": path.visible_lessons,
        },
    )


def _published_lesson(path_slug, lesson_slug):
    """Return a published lesson only from a published path."""
    return get_object_or_404(
        Lesson.objects.select_related("learning_path").prefetch_related("questions"),
        slug=lesson_slug,
        learning_path__slug=path_slug,
        learning_path__is_published=True,
        is_published=True,
    )


def _refresh_progress(user, lesson):
    """Recalculate saved progress from validated response rows."""
    total = LessonQuestion.objects.filter(lesson=lesson).count()
    responses = LessonResponse.objects.filter(user=user, question__lesson=lesson)
    answered = responses.count()
    correct = responses.filter(is_correct=True).count()

    progress, _ = LessonProgress.objects.get_or_create(user=user, lesson=lesson)
    progress.questions_total = total
    progress.questions_answered = answered
    progress.questions_correct = correct
    if total and answered == total and not progress.completed:
        progress.completed = True
    if progress.completed and not progress.completed_at:
        progress.completed_at = timezone.now()
    progress.save()
    return progress


def _progress_payload(progress):
    # A lesson marked complete by review is shown as 100% even if its knowledge
    # check has not been answered yet.
    percent = 100 if progress.completed else progress.percent
    return {
        "percent": percent,
        "progress_percent": percent,
        "completed": progress.completed,
        "questions_answered": progress.questions_answered,
        "questions_correct": progress.questions_correct,
        "questions_total": progress.questions_total,
    }


def lesson_detail(request, path_slug, lesson_slug):
    """Render the multimedia classroom for one published lesson."""
    lesson = _published_lesson(path_slug, lesson_slug)
    path = lesson.learning_path
    add_path_visuals([path])

    questions = list(lesson.questions.all())
    siblings = list(
        Lesson.objects.filter(learning_path=path, is_published=True).order_by(
            "order", "title"
        )
    )
    position = next(
        (index for index, item in enumerate(siblings) if item.pk == lesson.pk), -1
    )

    progress = None
    if request.user.is_authenticated:
        responses = {
            item.question_id: item
            for item in LessonResponse.objects.filter(
                user=request.user, question__lesson=lesson
            )
        }
        for question in questions:
            question.user_response = responses.get(question.pk)
        progress = _refresh_progress(request.user, lesson)

    takeaways = []
    for line in lesson.key_takeaways.splitlines():
        cleaned = line.strip().lstrip("•-*").strip()
        if cleaned:
            takeaways.append(cleaned)

    video_src = ""
    video_type = ""
    if lesson.video_file:
        video_src = lesson.video_file.url
        video_name = lesson.video_file.name
    elif lesson.video_url:
        video_src = lesson.video_url
        video_name = urlparse(lesson.video_url).path
    else:
        video_name = ""

    video_type = {
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".ogg": "video/ogg",
        ".ogv": "video/ogg",
    }.get(Path(video_name).suffix.lower(), "")

    context = {
        "path": path,
        "lesson": lesson,
        "questions": questions,
        "previous_lesson": siblings[position - 1] if position > 0 else None,
        "next_lesson": siblings[position + 1] if 0 <= position < len(siblings) - 1 else None,
        "progress": _progress_payload(progress) if progress else None,
        "can_save_progress": request.user.is_authenticated,
        "video_src": video_src,
        "video_type": video_type,
        "captions_src": lesson.captions_vtt.url if lesson.captions_vtt else "",
        "narration_text": lesson.narration_text or lesson.transcript,
        "transcript": lesson.transcript or lesson.narration_text,
        "takeaways": takeaways,
        "lesson_position": position + 1 if position >= 0 else 1,
        "lesson_total": len(siblings),
    }
    return render(request, "learning/lesson_detail.html", context)


@require_POST
@login_required
def lesson_question_answer(request, path_slug, lesson_slug):
    """Validate one answer server-side and return immediate feedback."""
    lesson = _published_lesson(path_slug, lesson_slug)
    question_id = request.POST.get("question_id", "")
    choice = request.POST.get("choice", "")

    if not question_id.isdigit() or not choice.isdigit():
        return JsonResponse({"error": "Choose one answer before submitting."}, status=400)

    question = get_object_or_404(
        LessonQuestion, pk=int(question_id), lesson=lesson
    )
    choice_value = int(choice)
    if choice_value not in LessonQuestion.Choice.values:
        return JsonResponse({"error": "That answer is not valid."}, status=400)

    is_correct = choice_value == question.correct_choice
    LessonResponse.objects.update_or_create(
        user=request.user,
        question=question,
        defaults={
            "selected_choice": choice_value,
            "is_correct": is_correct,
        },
    )
    progress = _refresh_progress(request.user, lesson)

    return JsonResponse(
        {
            "correct": is_correct,
            "explanation": question.explanation,
            "correct_choice": question.correct_choice,
            "correct_answer": question.correct_answer(),
            "progress_percent": 100 if progress.completed else progress.percent,
            "questions_answered": progress.questions_answered,
            "questions_correct": progress.questions_correct,
            "questions_total": progress.questions_total,
            "completed": progress.completed,
        }
    )


@require_POST
@login_required
def lesson_complete(request, path_slug, lesson_slug):
    """Let a learner mark a text-only or reviewed lesson complete."""
    lesson = _published_lesson(path_slug, lesson_slug)
    progress = _refresh_progress(request.user, lesson)
    progress.completed = True
    if not progress.completed_at:
        progress.completed_at = timezone.now()
    progress.save()
    return JsonResponse(_progress_payload(progress))

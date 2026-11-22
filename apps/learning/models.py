from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse

from .validators import (
    validate_lesson_caption_file,
    validate_lesson_video_file,
    validate_lesson_video_url,
)


class LearningPath(models.Model):
    """A published or draft pathway containing multiple ordered lessons."""

    class Difficulty(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BEGINNER,
    )
    # Stored in minutes so it uses the same unit as Lesson.estimated_minutes.
    estimated_duration = models.PositiveIntegerField(
        default=60,
        help_text="Estimated total duration in minutes.",
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "learning path"
        verbose_name_plural = "learning paths"
        constraints = [
            models.CheckConstraint(
                condition=Q(
                    difficulty__in=["beginner", "intermediate", "advanced"]
                ),
                name="valid_learning_path_difficulty",
            ),
            models.CheckConstraint(
                condition=Q(estimated_duration__gt=0),
                name="positive_learning_path_duration",
            ),
        ]

    def __str__(self):
        return self.title


class LessonVisualFocus(models.TextChoices):
    """Presentation-only animation selected for a lesson."""

    NONE = "none", "No animation"
    PHISHING = "phishing", "Phishing email inspection"
    PASSWORD = "password", "Password strength comparison"
    PRIVACY = "privacy", "Privacy settings"
    NETWORK = "network", "Network path and firewall"
    MOBILE = "mobile", "App permissions"
    DATA = "data", "Backup and recovery"


class Lesson(models.Model):
    """A single lesson that belongs to one learning path."""

    learning_path = models.ForeignKey(
        LearningPath,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)

    # Video classroom media. Either field may be used, but not both at once.
    video_file = models.FileField(
        upload_to="lesson-videos/",
        blank=True,
        validators=[validate_lesson_video_file],
        help_text="Upload an MP4, WebM or Ogg video up to 250 MB.",
    )
    video_url = models.URLField(
        blank=True,
        validators=[validate_lesson_video_url],
        help_text=(
            "Optional direct HTTP(S) URL to an MP4, WebM or Ogg video you own or "
            "are licensed to use."
        ),
    )
    captions_vtt = models.FileField(
        upload_to="lesson-captions/",
        blank=True,
        validators=[validate_lesson_caption_file],
        help_text="Optional WebVTT (.vtt) caption track for the video.",
    )

    # QuestMate narration and classroom text.
    narration_text = models.TextField(
        blank=True,
        help_text="Text read aloud by the browser's local speech synthesis.",
    )
    transcript = models.TextField(
        blank=True,
        help_text="Captions/transcript shown with the lesson player.",
    )
    key_takeaways = models.TextField(
        blank=True,
        help_text="One takeaway per line. Lines may start with a dash or bullet.",
    )
    visual_focus = models.CharField(
        max_length=20,
        choices=LessonVisualFocus.choices,
        default=LessonVisualFocus.NONE,
        help_text="Educational animation shown beside the video classroom.",
    )

    order = models.PositiveIntegerField(
        default=1,
        help_text="Display order within the learning path.",
    )
    estimated_minutes = models.PositiveIntegerField(
        default=10,
        help_text="Estimated time needed to complete this lesson in minutes.",
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["learning_path__title", "order", "title"]
        verbose_name = "lesson"
        verbose_name_plural = "lessons"
        constraints = [
            models.UniqueConstraint(
                fields=["learning_path", "slug"],
                name="unique_lesson_slug_per_path",
            ),
            models.CheckConstraint(
                condition=Q(order__gte=1),
                name="positive_lesson_order",
            ),
            models.CheckConstraint(
                condition=Q(estimated_minutes__gt=0),
                name="positive_lesson_estimated_minutes",
            ),
        ]

    def clean(self):
        """Prevent conflicting video sources on the same lesson."""
        super().clean()
        if self.video_file and self.video_url:
            raise ValidationError(
                {"video_url": "Choose either an uploaded video or a video URL, not both."}
            )

    def get_absolute_url(self):
        return reverse(
            "lesson_detail",
            args=[self.learning_path.slug, self.slug],
        )

    @property
    def has_video(self):
        return bool(self.video_file or self.video_url)

    def __str__(self):
        return f"{self.title} ({self.learning_path.title})"


class LessonQuestion(models.Model):
    """A multiple-choice knowledge-check question attached to a lesson."""

    class Choice(models.IntegerChoices):
        A = 1, "A"
        B = 2, "B"
        C = 3, "C"
        D = 4, "D"

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    prompt = models.TextField()
    choice_a = models.CharField(max_length=255)
    choice_b = models.CharField(max_length=255)
    choice_c = models.CharField(max_length=255)
    choice_d = models.CharField(max_length=255)
    correct_choice = models.PositiveSmallIntegerField(
        choices=Choice.choices,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
    )
    explanation = models.TextField(
        blank=True,
        help_text="Shown after the learner submits an answer.",
    )
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["lesson", "order", "id"]
        verbose_name = "lesson question"
        verbose_name_plural = "lesson questions"
        constraints = [
            models.UniqueConstraint(
                fields=["lesson", "order"],
                name="unique_lesson_question_order",
            ),
            models.CheckConstraint(
                condition=Q(order__gte=1),
                name="positive_lesson_question_order",
            ),
        ]

    def choices(self):
        return [
            (self.Choice.A.value, self.choice_a),
            (self.Choice.B.value, self.choice_b),
            (self.Choice.C.value, self.choice_c),
            (self.Choice.D.value, self.choice_d),
        ]

    def correct_answer(self):
        return dict(self.choices()).get(self.correct_choice, "")

    def __str__(self):
        return f"{self.lesson.title}: {self.prompt[:60]}"


class LessonProgress(models.Model):
    """Saved progress for one signed-in learner and one lesson."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_progress",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="progress_records",
    )
    completed = models.BooleanField(default=False)
    questions_answered = models.PositiveSmallIntegerField(default=0)
    questions_correct = models.PositiveSmallIntegerField(default=0)
    questions_total = models.PositiveSmallIntegerField(default=0)
    last_viewed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-last_viewed"]
        verbose_name = "lesson progress"
        verbose_name_plural = "lesson progress"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "lesson"],
                name="unique_user_lesson_progress",
            )
        ]

    @property
    def percent(self):
        if self.completed and not self.questions_total:
            return 100
        if not self.questions_total:
            return 0
        return min(100, round((self.questions_answered / self.questions_total) * 100))

    def __str__(self):
        return f"{self.user}: {self.lesson.title} ({self.percent}%)"


class LessonResponse(models.Model):
    """A learner's saved answer to one lesson question."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_responses",
    )
    question = models.ForeignKey(
        LessonQuestion,
        on_delete=models.CASCADE,
        related_name="responses",
    )
    selected_choice = models.PositiveSmallIntegerField(
        choices=LessonQuestion.Choice.choices,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
    )
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-answered_at"]
        verbose_name = "lesson response"
        verbose_name_plural = "lesson responses"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "question"],
                name="unique_user_lesson_response",
            )
        ]

    def __str__(self):
        return f"{self.user}: {self.question_id} ({'correct' if self.is_correct else 'review'})"

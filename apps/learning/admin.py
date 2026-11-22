from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import LearningPath, Lesson, LessonQuestion


class LessonAdminForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("video_file") and cleaned_data.get("video_url"):
            raise ValidationError(
                "Choose either an uploaded video or an external video URL, not both."
            )
        return cleaned_data


class LessonQuestionInline(admin.TabularInline):
    model = LessonQuestion
    extra = 1
    min_num = 0
    fields = (
        "prompt",
        "choice_a",
        "choice_b",
        "choice_c",
        "choice_d",
        "correct_choice",
        "explanation",
        "order",
    )


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "difficulty",
        "estimated_duration",
        "is_published",
        "created_at",
    )
    list_filter = ("difficulty", "is_published", "created_at")
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    ordering = ("title",)
    list_per_page = 20


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    inlines = (LessonQuestionInline,)

    list_display = (
        "title",
        "learning_path",
        "order",
        "has_video",
        "estimated_minutes",
        "is_published",
    )
    list_filter = ("learning_path", "is_published", "visual_focus")
    search_fields = (
        "title",
        "slug",
        "description",
        "content",
        "narration_text",
        "learning_path__title",
    )
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    ordering = ("learning_path__title", "order", "title")
    list_select_related = ("learning_path",)
    list_per_page = 20

    fieldsets = (
        (
            "Lesson content",
            {
                "fields": (
                    "learning_path",
                    "title",
                    "slug",
                    "description",
                    "content",
                    "order",
                    "estimated_minutes",
                    "is_published",
                )
            },
        ),
        (
            "Video classroom",
            {
                "fields": ("video_file", "video_url", "captions_vtt"),
                "description": (
                    "Upload your own video or use a validated direct URL to a video "
                    "you own or are licensed to use. Choose one source, not both."
                ),
            },
        ),
        (
            "QuestMate narration",
            {
                "fields": ("narration_text", "transcript"),
                "description": "Narration uses the learner's local browser voices only.",
            },
        ),
        (
            "Learning activities",
            {
                "fields": ("key_takeaways", "visual_focus"),
                "description": "Add knowledge-check questions using the inline editor below.",
            },
        ),
        (
            "Dates",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(boolean=True, description="Video")
    def has_video(self, obj):
        return obj.has_video

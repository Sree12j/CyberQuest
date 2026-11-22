from io import StringIO
from pathlib import Path

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse

from .admin import LessonAdmin, LessonAdminForm, LessonQuestionInline
from .models import (
    LearningPath,
    Lesson,
    LessonProgress,
    LessonQuestion,
    LessonResponse,
    LessonVisualFocus,
)
from .templatetags.lesson_notes import lesson_notes
from .validators import (
    validate_lesson_caption_file,
    validate_lesson_video_file,
    validate_lesson_video_url,
)

User = get_user_model()


class LearningPathModelTests(TestCase):
    """Checks for the LearningPath model."""

    def setUp(self):
        self.path = LearningPath.objects.create(
            title="Security Basics",
            slug="security-basics",
            description="Learn the foundations of cybersecurity.",
            difficulty=LearningPath.Difficulty.BEGINNER,
            estimated_duration=120,
            is_published=True,
        )

    def test_learning_path_creation(self):
        self.assertEqual(self.path.title, "Security Basics")
        self.assertEqual(self.path.difficulty, "beginner")
        self.assertTrue(self.path.is_published)
        self.assertEqual(str(self.path), "Security Basics")

    def test_slug_is_saved(self):
        saved_path = LearningPath.objects.get(pk=self.path.pk)
        self.assertEqual(saved_path.slug, "security-basics")

    def test_difficulty_is_valid(self):
        self.path.full_clean()
        valid_values = [choice[0] for choice in LearningPath.Difficulty.choices]
        self.assertIn(self.path.difficulty, valid_values)
        self.assertEqual(self.path.get_difficulty_display(), "Beginner")

        invalid_path = LearningPath(
            title="Invalid Path",
            slug="invalid-path",
            description="This difficulty is not allowed.",
            difficulty="expert",
        )
        with self.assertRaises(ValidationError):
            invalid_path.full_clean()


class LessonModelTests(TestCase):
    """Checks for the Lesson model."""

    def setUp(self):
        self.path = LearningPath.objects.create(
            title="Security Basics",
            slug="security-basics",
            description="Learn the foundations of cybersecurity.",
        )
        self.other_path = LearningPath.objects.create(
            title="Networking Basics",
            slug="networking-basics",
            description="Learn how networks work.",
        )

    def test_lesson_is_associated_with_learning_path(self):
        lesson = Lesson.objects.create(
            learning_path=self.path,
            title="What is cybersecurity?",
            slug="what-is-cybersecurity",
            order=1,
        )
        self.assertEqual(lesson.learning_path, self.path)
        self.assertIn(lesson, self.path.lessons.all())

    def test_lesson_ordering(self):
        Lesson.objects.create(
            learning_path=self.path,
            title="Third lesson",
            slug="third-lesson",
            order=3,
        )
        Lesson.objects.create(
            learning_path=self.path,
            title="First lesson",
            slug="first-lesson",
            order=1,
        )
        Lesson.objects.create(
            learning_path=self.path,
            title="Second lesson",
            slug="second-lesson",
            order=2,
        )

        titles = list(
            Lesson.objects.filter(learning_path=self.path).values_list(
                "title", flat=True
            )
        )
        self.assertEqual(titles, ["First lesson", "Second lesson", "Third lesson"])

    def test_lesson_slug_unique_within_learning_path(self):
        Lesson.objects.create(
            learning_path=self.path,
            title="Introduction",
            slug="introduction",
            order=1,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Lesson.objects.create(
                    learning_path=self.path,
                    title="Duplicate introduction",
                    slug="introduction",
                    order=2,
                )

    def test_same_lesson_slug_allowed_in_different_learning_path(self):
        Lesson.objects.create(
            learning_path=self.path,
            title="Introduction",
            slug="introduction",
            order=1,
        )
        other_lesson = Lesson.objects.create(
            learning_path=self.other_path,
            title="Introduction",
            slug="introduction",
            order=1,
        )
        self.assertEqual(other_lesson.learning_path, self.other_path)

    def test_learning_path_slug_is_unique(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                LearningPath.objects.create(
                    title="Duplicate Slug Path",
                    slug="security-basics",
                    description="This slug is already used.",
                )


class SeedLearningPathsCommandTests(TestCase):
    """Checks that the Day 5 seed command is safe to run repeatedly."""

    def test_seed_command_creates_six_paths_and_eighteen_lessons(self):
        output = StringIO()
        call_command("seed_learning_paths", stdout=output)

        self.assertEqual(LearningPath.objects.count(), 6)
        self.assertEqual(Lesson.objects.count(), 18)
        self.assertEqual(LessonQuestion.objects.count(), 36)
        self.assertEqual(LearningPath.objects.filter(is_published=True).count(), 6)
        self.assertEqual(Lesson.objects.filter(is_published=True).count(), 18)
        self.assertEqual(
            Lesson.objects.filter(visual_focus=LessonVisualFocus.PHISHING).count(), 3
        )
        self.assertTrue(
            Lesson.objects.filter(narration_text__startswith="Welcome to").exists()
        )

        phishing = LearningPath.objects.get(slug="phishing-detective")
        self.assertEqual(phishing.lessons.count(), 3)
        self.assertIn("6 new path(s)", output.getvalue())
        self.assertIn("18 new lesson(s)", output.getvalue())

    def test_seed_command_twice_does_not_create_duplicates(self):
        call_command("seed_learning_paths", stdout=StringIO())
        output = StringIO()
        call_command("seed_learning_paths", stdout=output)

        self.assertEqual(LearningPath.objects.count(), 6)
        self.assertEqual(Lesson.objects.count(), 18)
        self.assertEqual(LessonQuestion.objects.count(), 36)
        self.assertIn("0 new path(s)", output.getvalue())
        self.assertIn("0 new lesson(s)", output.getvalue())


class LearningPathListPageTests(TestCase):
    """Checks the database-backed learning catalog."""

    def setUp(self):
        self.published = LearningPath.objects.create(
            title="Published Path",
            slug="published-path",
            description="A path that visitors can see.",
            is_published=True,
        )
        self.unpublished = LearningPath.objects.create(
            title="Hidden Path",
            slug="hidden-path",
            description="A draft path that visitors must not see.",
            is_published=False,
        )
        self.list_url = reverse("learning_paths")

    def test_learning_paths_page_returns_200(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "learning/paths_placeholder.html")
        self.assertContains(response, "Explore Cybersecurity Learning Paths")

    def test_published_paths_appear_and_unpublished_paths_are_excluded(self):
        response = self.client.get(self.list_url)
        self.assertContains(response, "Published Path")
        self.assertNotContains(response, "Hidden Path")
        self.assertContains(response, reverse("learning_path_detail", args=[self.published.slug]))

    def test_empty_state_when_no_paths_are_published(self):
        LearningPath.objects.all().delete()
        response = self.client.get(self.list_url)
        self.assertContains(response, "No published paths yet")


class LearningPathDetailPageTests(TestCase):
    """Checks published path details and lesson visibility."""

    def setUp(self):
        self.path = LearningPath.objects.create(
            title="Phishing Detective",
            slug="phishing-detective",
            description="Learn to recognize phishing messages.",
            is_published=True,
        )
        self.hidden_path = LearningPath.objects.create(
            title="Hidden Path",
            slug="hidden-path",
            description="Draft content.",
            is_published=False,
        )
        Lesson.objects.create(
            learning_path=self.path,
            title="Second Lesson",
            slug="second-lesson",
            description="Shown second.",
            order=2,
            is_published=True,
        )
        Lesson.objects.create(
            learning_path=self.path,
            title="First Lesson",
            slug="first-lesson",
            description="Shown first.",
            order=1,
            is_published=True,
        )
        Lesson.objects.create(
            learning_path=self.path,
            title="Hidden Lesson",
            slug="hidden-lesson",
            description="Must not be shown.",
            order=3,
            is_published=False,
        )
        self.detail_url = reverse("learning_path_detail", args=[self.path.slug])

    def test_valid_published_path_returns_200(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "learning/path_detail.html")
        self.assertContains(response, "Phishing Detective")
        self.assertContains(response, "All Learning Paths")
        self.assertContains(response, reverse("learning_paths"))

    def test_lessons_appear_in_order_and_unpublished_lessons_are_hidden(self):
        response = self.client.get(self.detail_url)
        content = response.content.decode()
        self.assertContains(response, "First Lesson")
        self.assertContains(response, "Second Lesson")
        self.assertNotContains(response, "Hidden Lesson")
        self.assertLess(content.index("First Lesson"), content.index("Second Lesson"))
        self.assertEqual(response.context["path"].published_lesson_count, 2)

    def test_unpublished_path_returns_404(self):
        response = self.client.get(
            reverse("learning_path_detail", args=[self.hidden_path.slug])
        )
        self.assertEqual(response.status_code, 404)

    def test_invalid_slug_returns_404(self):
        response = self.client.get(
            reverse("learning_path_detail", args=["does-not-exist"])
        )
        self.assertEqual(response.status_code, 404)


class LearningAdminTests(TestCase):
    """Checks that content editors keep the Day 2 admin registrations."""

    def test_learning_models_are_registered_in_admin(self):
        self.assertIn(LearningPath, admin.site._registry)
        self.assertIn(Lesson, admin.site._registry)
        self.assertIn("difficulty", admin.site._registry[LearningPath].list_filter)
        self.assertIn("order", admin.site._registry[Lesson].list_display)


class FakeUpload:
    """Small upload double for size/header validation checks."""

    def __init__(self, name, size, content_type, header):
        self.name = name
        self.size = size
        self.content_type = content_type
        self.header = header

    def tell(self):
        return 0

    def read(self, length):
        return self.header[:length]

    def seek(self, position):
        return position


class LessonMediaValidationTests(TestCase):
    """Uploads and external URLs must be constrained before reaching storage."""

    def test_valid_mp4_upload_is_accepted(self):
        upload = SimpleUploadedFile(
            "lesson.mp4",
            b"\x00\x00\x00\x18ftypmp42test",
            content_type="video/mp4",
        )
        validate_lesson_video_file(upload)
        self.assertEqual(upload.read(12)[4:8], b"ftyp")

    def test_valid_webm_and_ogg_uploads_are_accepted(self):
        validate_lesson_video_file(
            SimpleUploadedFile(
                "lesson.webm",
                b"\x1a\x45\xdf\xa3data",
                content_type="video/webm",
            )
        )
        validate_lesson_video_file(
            SimpleUploadedFile(
                "lesson.ogg", b"OggSdata", content_type="video/ogg"
            )
        )

    def test_invalid_video_extension_is_rejected(self):
        upload = SimpleUploadedFile("lesson.exe", b"ftyp", content_type="video/mp4")
        with self.assertRaises(ValidationError):
            validate_lesson_video_file(upload)

    def test_fake_mp4_header_is_rejected(self):
        upload = SimpleUploadedFile("lesson.mp4", b"not-a-video", content_type="video/mp4")
        with self.assertRaises(ValidationError):
            validate_lesson_video_file(upload)

    def test_oversized_video_is_rejected(self):
        upload = FakeUpload(
            "lesson.mp4",
            251 * 1024 * 1024,
            "video/mp4",
            b"\x00\x00\x00\x18ftypmp42",
        )
        with self.assertRaises(ValidationError):
            validate_lesson_video_file(upload)

    def test_webvtt_caption_validation(self):
        valid = SimpleUploadedFile(
            "en.vtt",
            b"WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nWelcome.",
            content_type="text/vtt",
        )
        validate_lesson_caption_file(valid)

        invalid = SimpleUploadedFile("notes.txt", b"WEBVTT", content_type="text/plain")
        with self.assertRaises(ValidationError):
            validate_lesson_caption_file(invalid)

        not_vtt = SimpleUploadedFile("en.vtt", b"Just text", content_type="text/vtt")
        with self.assertRaises(ValidationError):
            validate_lesson_caption_file(not_vtt)

    def test_direct_video_url_is_accepted(self):
        validate_lesson_video_url("https://media.example.com/lessons/intro.mp4")

    def test_video_url_scheme_and_extension_are_validated(self):
        for value in (
            "javascript:alert(1)",
            "https://media.example.com/lessons/page.html",
            "https://user:pass@media.example.com/lesson.mp4",
        ):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                validate_lesson_video_url(value)

    @override_settings(LESSON_VIDEO_ALLOWED_HOSTS=["approved.example.com"])
    def test_configured_video_host_allowlist_is_enforced(self):
        validate_lesson_video_url("https://approved.example.com/lesson.mp4")
        with self.assertRaises(ValidationError):
            validate_lesson_video_url("https://other.example.com/lesson.mp4")


class LessonQuestionAndProgressModelTests(TestCase):
    def setUp(self):
        self.path = LearningPath.objects.create(
            title="Classroom Path",
            slug="classroom-path",
            description="Path for classroom tests.",
            is_published=True,
        )
        self.lesson = Lesson.objects.create(
            learning_path=self.path,
            title="Classroom Lesson",
            slug="classroom-lesson",
            content="Lesson text.",
            order=1,
            is_published=True,
        )
        self.user = User.objects.create_user(
            username="classroomlearner",
            password="CyberQuest2026!Secure",
            display_name="Classroom Learner",
        )

    def test_lesson_defaults_and_absolute_url(self):
        self.assertFalse(self.lesson.has_video)
        self.assertEqual(self.lesson.visual_focus, LessonVisualFocus.NONE)
        self.assertEqual(
            self.lesson.get_absolute_url(),
            reverse("lesson_detail", args=[self.path.slug, self.lesson.slug]),
        )

    def test_conflicting_video_sources_fail_validation(self):
        self.lesson.video_file = "lesson-videos/lesson.mp4"
        self.lesson.video_url = "https://media.example.com/lesson.mp4"
        with self.assertRaises(ValidationError) as context:
            self.lesson.clean()
        self.assertIn("video_url", context.exception.message_dict)

    def test_question_choices_and_correct_answer(self):
        question = LessonQuestion.objects.create(
            lesson=self.lesson,
            prompt="Which choice is correct?",
            choice_a="A choice",
            choice_b="B choice",
            choice_c="C choice",
            choice_d="D choice",
            correct_choice=2,
            explanation="B is the correct answer.",
            order=1,
        )
        self.assertEqual(len(question.choices()), 4)
        self.assertEqual(question.correct_answer(), "B choice")
        self.assertEqual(str(question.correct_choice), "2")

    def test_progress_percent(self):
        progress = LessonProgress.objects.create(
            user=self.user,
            lesson=self.lesson,
            questions_total=4,
            questions_answered=3,
        )
        self.assertEqual(progress.percent, 75)
        progress.completed = True
        self.assertEqual(progress.percent, 75)
        progress.questions_total = 0
        self.assertEqual(progress.percent, 100)


class LessonNotesFilterTests(TestCase):
    def test_notes_are_structured_and_escaped(self):
        html = lesson_notes(
            "Quick checklist:\n"
            "• Check the sender <script>alert(1)</script>\n"
            "Tip: Verify through the official app."
        )
        self.assertIn("<h3>Quick checklist</h3>", html)
        self.assertIn('<ul class="cq-note-list">', html)
        self.assertIn("cq-callout-tip", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)


class LessonClassroomViewTests(TestCase):
    def setUp(self):
        self.path = LearningPath.objects.create(
            title="Phishing Detective",
            slug="phishing-detective",
            description="Learn to spot phishing.",
            is_published=True,
        )
        self.lesson = Lesson.objects.create(
            learning_path=self.path,
            title="Spot the Signs",
            slug="spot-the-signs",
            description="Inspect a suspicious email.",
            content="Sender inconsistencies\nCheck the full sender address.",
            narration_text="Welcome. Check the full sender address before you click.",
            transcript="Full transcript text.",
            key_takeaways="- Check the sender\n- Hover over links",
            visual_focus=LessonVisualFocus.PHISHING,
            order=1,
            is_published=True,
        )
        self.question = LessonQuestion.objects.create(
            lesson=self.lesson,
            prompt="What should you inspect first?",
            choice_a="The wallpaper",
            choice_b="The full sender address",
            choice_c="The font size",
            choice_d="The time of day",
            correct_choice=2,
            explanation="Display names can be faked, so check the full address.",
            order=1,
        )
        self.user = User.objects.create_user(
            username="lessonviewer",
            password="CyberQuest2026!Secure",
            display_name="Lesson Viewer",
        )
        self.url = reverse(
            "lesson_detail", args=[self.path.slug, self.lesson.slug]
        )

    def test_published_lesson_opens_without_video(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "learning/lesson_detail.html")
        self.assertContains(response, "Spot the Signs")
        self.assertContains(response, "Text lesson · no video assigned yet")
        self.assertContains(response, "QuestMate")
        self.assertContains(response, "What should you inspect first?")
        self.assertNotContains(response, "Correct answer:")
        self.assertEqual(response.context["video_src"], "")

    def test_video_url_and_caption_track_render_when_assigned(self):
        self.lesson.video_url = "https://media.example.com/lesson.mp4"
        self.lesson.captions_vtt = "lesson-captions/english.vtt"
        self.lesson.save()

        response = self.client.get(self.url)
        self.assertContains(response, "https://media.example.com/lesson.mp4")
        self.assertContains(response, 'kind="captions"')
        self.assertContains(response, "/media/lesson-captions/english.vtt")
        self.assertContains(response, "Playback speed")

    def test_visual_animations_and_takeaways_render(self):
        response = self.client.get(self.url)
        content = response.content.decode()
        self.assertIn("cq-anim-phishing", content)
        for absent in (
            "cq-anim-password",
            "cq-anim-privacy",
            "cq-anim-network",
            "cq-anim-mobile",
            "cq-anim-data",
        ):
            with self.subTest(absent=absent):
                self.assertNotIn(absent, content)
        self.assertContains(response, "Hover over links")

    def test_unpublished_lesson_and_path_are_hidden(self):
        self.lesson.is_published = False
        self.lesson.save()
        self.assertEqual(self.client.get(self.url).status_code, 404)

        self.lesson.is_published = True
        self.lesson.save()
        self.path.is_published = False
        self.path.save()
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_previous_and_next_lessons_are_in_context(self):
        self.lesson.order = 2
        self.lesson.save(update_fields=["order"])
        previous = Lesson.objects.create(
            learning_path=self.path,
            title="First Lesson",
            slug="first-lesson",
            order=1,
            is_published=True,
        )
        next_lesson = Lesson.objects.create(
            learning_path=self.path,
            title="Next Lesson",
            slug="next-lesson",
            order=3,
            is_published=True,
        )
        response = self.client.get(self.url)
        self.assertEqual(response.context["previous_lesson"].pk, previous.pk)
        self.assertEqual(response.context["next_lesson"].pk, next_lesson.pk)

    def test_anonymous_visitor_sees_login_notice(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Sign in to save progress")
        self.assertContains(response, reverse("login"))
        self.assertFalse(response.context["can_save_progress"])


class LessonKnowledgeCheckTests(TestCase):
    def setUp(self):
        self.path = LearningPath.objects.create(
            title="Classroom Path",
            slug="classroom-path",
            description="Path for knowledge checks.",
            is_published=True,
        )
        self.lesson = Lesson.objects.create(
            learning_path=self.path,
            title="Check Lesson",
            slug="check-lesson",
            order=1,
            is_published=True,
        )
        self.question = LessonQuestion.objects.create(
            lesson=self.lesson,
            prompt="Pick the safe action.",
            choice_a="Click the link",
            choice_b="Verify independently",
            choice_c="Reply immediately",
            choice_d="Delete your account",
            correct_choice=2,
            explanation="A trusted route avoids the suspicious message.",
            order=1,
        )
        self.user = User.objects.create_user(
            username="quizlearner",
            password="CyberQuest2026!Secure",
            display_name="Quiz Learner",
        )
        self.answer_url = reverse(
            "lesson_question_answer", args=[self.path.slug, self.lesson.slug]
        )

    def test_anonymous_answer_submission_requires_login(self):
        response = self.client.post(
            self.answer_url,
            {"question_id": self.question.pk, "choice": 2},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])
        self.assertFalse(LessonResponse.objects.exists())

    def test_correct_answer_is_validated_and_saves_progress(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.answer_url,
            {"question_id": self.question.pk, "choice": 2},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["correct"])
        self.assertEqual(data["progress_percent"], 100)
        self.assertEqual(data["questions_correct"], 1)
        self.assertIn("trusted route", data["explanation"])
        self.assertEqual(LessonResponse.objects.count(), 1)
        progress = LessonProgress.objects.get(user=self.user, lesson=self.lesson)
        self.assertTrue(progress.completed)
        self.assertIsNotNone(progress.completed_at)

    def test_incorrect_answer_gets_explanation_and_no_score(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.answer_url,
            {"question_id": self.question.pk, "choice": 1},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = response.json()
        self.assertFalse(data["correct"])
        self.assertEqual(data["correct_choice"], 2)
        self.assertEqual(data["correct_answer"], "Verify independently")
        self.assertEqual(LessonProgress.objects.get(user=self.user, lesson=self.lesson).questions_correct, 0)

    def test_invalid_question_and_choice_are_rejected(self):
        self.client.force_login(self.user)
        invalid_question = self.client.post(
            self.answer_url, {"question_id": 9999, "choice": 1}
        )
        self.assertEqual(invalid_question.status_code, 404)

        other_lesson = Lesson.objects.create(
            learning_path=self.path,
            title="Other Lesson",
            slug="other-lesson",
            order=2,
            is_published=True,
        )
        foreign_question = LessonQuestion.objects.create(
            lesson=other_lesson,
            prompt="Foreign question?",
            choice_a="A",
            choice_b="B",
            choice_c="C",
            choice_d="D",
            correct_choice=1,
            order=1,
        )
        foreign = self.client.post(
            self.answer_url,
            {"question_id": foreign_question.pk, "choice": 1},
        )
        self.assertEqual(foreign.status_code, 404)

        bad_choice = self.client.post(
            self.answer_url, {"question_id": self.question.pk, "choice": 9}
        )
        self.assertEqual(bad_choice.status_code, 400)
        self.assertFalse(LessonResponse.objects.exists())

    def test_reanswering_updates_one_response_without_duplicate_scoring(self):
        self.client.force_login(self.user)
        self.client.post(
            self.answer_url, {"question_id": self.question.pk, "choice": 1}
        )
        self.client.post(
            self.answer_url, {"question_id": self.question.pk, "choice": 2}
        )
        self.assertEqual(LessonResponse.objects.count(), 1)
        progress = LessonProgress.objects.get(user=self.user, lesson=self.lesson)
        self.assertEqual(progress.questions_answered, 1)
        self.assertEqual(progress.questions_correct, 1)

    def test_mark_complete_endpoint_saves_progress(self):
        complete_url = reverse(
            "lesson_complete", args=[self.path.slug, self.lesson.slug]
        )
        anonymous = self.client.post(complete_url)
        self.assertEqual(anonymous.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.post(complete_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["percent"], 100)
        progress = LessonProgress.objects.get(user=self.user, lesson=self.lesson)
        self.assertTrue(progress.completed)


class LessonAdminMediaTests(TestCase):
    def setUp(self):
        self.path = LearningPath.objects.create(
            title="Admin Path",
            slug="admin-path",
            description="Admin test path.",
        )
        self.lesson = Lesson.objects.create(
            learning_path=self.path,
            title="Admin Lesson",
            slug="admin-lesson",
            order=1,
        )

    def test_question_inline_is_registered(self):
        self.assertIn(LessonQuestionInline, LessonAdmin.inlines)
        self.assertIn("has_video", LessonAdmin.list_display)
        self.assertIn("video_file", LessonAdmin.fieldsets[1][1]["fields"])

    def test_admin_form_rejects_conflicting_video_sources(self):
        form = LessonAdminForm(instance=self.lesson)
        form.cleaned_data = {
            "video_file": "lesson-videos/demo.mp4",
            "video_url": "https://media.example.com/demo.mp4",
        }
        with self.assertRaises(ValidationError):
            form.clean()


class LessonScriptLocalOnlyTests(TestCase):
    def test_lesson_script_uses_same_origin_fetch_only(self):
        js_path = Path(__file__).resolve().parents[2] / "static" / "js" / "lesson.js"
        content = js_path.read_text(encoding="utf-8")
        for forbidden in (
            "localStorage",
            "sessionStorage",
            "XMLHttpRequest",
            "https://",
            "http://",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, content)
        self.assertIn("speechSynthesis", content)
        self.assertIn("fetch(", content)

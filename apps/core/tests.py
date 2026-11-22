from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.learning.models import LearningPath, Lesson

User = get_user_model()


class HomePageTests(TestCase):
    """Basic checks for the Day 1 homepage."""

    def test_homepage_returns_200(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_homepage_contains_project_title(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "<title>CyberQuest</title>")

    def test_homepage_uses_expected_templates(self):
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "core/home.html")

    def test_homepage_shows_real_missions_and_published_paths(self):
        path = LearningPath.objects.create(
            title="Homepage Sample Path",
            slug="homepage-sample",
            description="A short published path for the homepage preview.",
            is_published=True,
        )
        Lesson.objects.create(
            learning_path=path,
            title="First lesson",
            slug="first-lesson",
            order=1,
            is_published=True,
        )

        response = self.client.get(reverse("home"))

        for title in (
            "Phishing Detective",
            "Password Guardian",
            "Privacy Protector",
            "Network Navigator",
        ):
            with self.subTest(title=title):
                self.assertContains(response, title)
        for url_name in (
            "phishing_briefing",
            "password_guardian_home",
            "privacy_protector_home",
            "network_navigator_home",
        ):
            with self.subTest(url_name=url_name):
                self.assertContains(response, reverse(url_name))

        self.assertContains(response, "Quick safety check")
        self.assertContains(response, "Local simulation ready.")
        self.assertContains(response, path.title)
        self.assertContains(
            response,
            reverse("learning_path_detail", args=[path.slug]),
        )
        self.assertContains(response, "1 lesson")
        self.assertContains(response, "published paths")
        self.assertContains(response, "guided lessons")

    def test_homepage_actions_match_authentication_state(self):
        anonymous = self.client.get(reverse("home"))
        self.assertContains(anonymous, reverse("login"))
        self.assertContains(anonymous, reverse("register"))
        self.assertNotContains(anonymous, reverse("dashboard"))

        user = User.objects.create_user(
            username="homelearner",
            password="CyberQuest2026!Secure",
            display_name="Home Learner",
        )
        self.client.force_login(user)
        authenticated = self.client.get(reverse("home"))

        self.assertContains(authenticated, reverse("challenge_home"))
        self.assertContains(authenticated, reverse("dashboard"))
        self.assertNotContains(authenticated, reverse("register"))

    def test_homepage_interaction_script_is_local_only(self):
        js_path = Path(__file__).resolve().parents[2] / "static" / "js" / "home.js"
        content = js_path.read_text(encoding="utf-8")

        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, content)


class DashboardViewTests(TestCase):
    """Day 4 dashboard tests, updated in Day 5 for database-backed paths."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="dashboardlearner",
            password="CyberQuest2026!Secure",
            display_name="Dashboard Explorer",
        )
        self.dashboard_url = reverse("dashboard")

        # Day 5: the dashboard reads real published paths from the database.
        self.path = LearningPath.objects.create(
            title="Phishing Detective",
            slug="phishing-detective",
            description="Learn to recognize suspicious messages.",
            difficulty=LearningPath.Difficulty.BEGINNER,
            is_published=True,
        )
        self.hidden_path = LearningPath.objects.create(
            title="Hidden Practice Path",
            slug="hidden-practice-path",
            description="A draft path that must not appear on the dashboard.",
            is_published=False,
        )
        Lesson.objects.create(
            learning_path=self.path,
            title="What Is Phishing?",
            slug="what-is-phishing",
            order=1,
            is_published=True,
        )

    def test_dashboard_url_works_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_user_cannot_access_dashboard(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)

        followed_response = self.client.get(self.dashboard_url, follow=True)
        self.assertTemplateUsed(followed_response, "accounts/login.html")
        self.assertNotContains(followed_response, "Dashboard Explorer")

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.get(self.dashboard_url)
        expected = f"{reverse('login')}?next={self.dashboard_url}"
        self.assertRedirects(response, expected)

    def test_authenticated_user_can_access_dashboard(self):
        self.client.force_login(self.user)
        response = self.client.get(self.dashboard_url)
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "core/dashboard.html")

    def test_dashboard_displays_correct_user_name(self):
        self.client.force_login(self.user)
        response = self.client.get(self.dashboard_url)
        self.assertContains(response, "Welcome back,")
        self.assertContains(response, "Dashboard Explorer")
        self.assertContains(response, "@dashboardlearner")

    def test_dashboard_demo_data_is_clearly_labelled(self):
        self.client.force_login(self.user)
        response = self.client.get(self.dashboard_url)
        self.assertContains(response, "Demonstration preview")
        self.assertContains(response, "DEMO")
        self.assertContains(response, "no API connected")

    def test_published_learning_paths_come_from_the_database(self):
        self.client.force_login(self.user)
        response = self.client.get(self.dashboard_url)
        self.assertContains(response, "Phishing Detective")
        self.assertContains(response, "Learn to recognize suspicious messages.")
        self.assertNotContains(response, "Hidden Practice Path")
        self.assertEqual(list(response.context["learning_paths"]), [self.path])

    def test_dashboard_path_card_links_to_detail_page(self):
        self.client.force_login(self.user)
        response = self.client.get(self.dashboard_url)
        detail_url = reverse("learning_path_detail", args=[self.path.slug])
        self.assertContains(response, f'href="{detail_url}"')
        self.assertContains(response, "Explore Path")

    def test_dashboard_shows_real_lesson_count_for_path(self):
        self.client.force_login(self.user)
        response = self.client.get(self.dashboard_url)
        self.assertContains(response, "1 lesson")

    def test_sidebar_links_and_logout_form_are_present(self):
        self.client.force_login(self.user)
        response = self.client.get(self.dashboard_url)
        self.assertContains(response, 'href="#learning-paths"')
        self.assertContains(response, f'href="{reverse("challenge_home")}"')
        self.assertContains(response, 'href="#achievements"')
        self.assertContains(response, 'href="#leaderboard"')
        self.assertContains(response, 'href="#questmate"')
        self.assertContains(response, f'href="{reverse("account_home")}"')
        self.assertContains(response, f'action="{reverse("logout")}" method="post"')
        self.assertContains(response, "Logout")

    def test_account_page_links_to_dashboard(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("account_home"))
        self.assertContains(response, f'href="{self.dashboard_url}"')

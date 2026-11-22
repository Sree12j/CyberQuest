from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

STRONG_PASSWORD = "CyberQuest2026!Secure"


class UserModelTests(TestCase):
    """Checks for the custom CyberQuest user model."""

    def test_user_can_be_created(self):
        user = User.objects.create_user(
            username="newlearner",
            password="StrongPass123!",
        )
        self.assertEqual(user.username, "newlearner")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_display_name_field(self):
        user = User.objects.create_user(
            username="cyber-explorer",
            password="StrongPass123!",
            display_name="Cyber Explorer",
        )
        self.assertEqual(user.display_name, "Cyber Explorer")
        self.assertEqual(str(user), "Cyber Explorer")

    def test_string_without_display_name_uses_username(self):
        user = User.objects.create_user(
            username="plainlearner",
            password="StrongPass123!",
        )
        self.assertEqual(str(user), "plainlearner")

    def test_timestamps_are_set(self):
        user = User.objects.create_user(
            username="timestamped",
            password="StrongPass123!",
        )
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)


class RegistrationViewTests(TestCase):
    """Day 3 registration flow tests."""

    def registration_data(self, **overrides):
        data = {
            "display_name": "New Learner",
            "username": "newquestuser",
            "email": "newquestuser@example.com",
            "password1": STRONG_PASSWORD,
            "password2": STRONG_PASSWORD,
        }
        data.update(overrides)
        return data

    def test_registration_page_returns_200(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")
        self.assertContains(response, "Create Your Account")

    def test_valid_registration_creates_user(self):
        response = self.client.post(reverse("register"), self.registration_data())
        self.assertRedirects(response, reverse("login"))

        user = User.objects.get(username="newquestuser")
        self.assertEqual(user.display_name, "New Learner")
        self.assertEqual(user.email, "newquestuser@example.com")

    def test_password_is_hashed(self):
        self.client.post(reverse("register"), self.registration_data())
        user = User.objects.get(username="newquestuser")
        self.assertNotEqual(user.password, STRONG_PASSWORD)
        self.assertTrue(user.check_password(STRONG_PASSWORD))

    def test_registration_does_not_log_user_in(self):
        self.client.post(reverse("register"), self.registration_data())
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_password_confirmation_mismatch_is_rejected(self):
        response = self.client.post(
            reverse("register"),
            self.registration_data(password2="DifferentPassword2026!"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newquestuser").exists())
        self.assertIn("password2", response.context["form"].errors)

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user(username="newquestuser", password=STRONG_PASSWORD)
        response = self.client.post(
            reverse("register"),
            self.registration_data(email="another@example.com"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="newquestuser").count(), 1)
        self.assertIn("username", response.context["form"].errors)

    def test_invalid_email_is_rejected(self):
        response = self.client.post(
            reverse("register"),
            self.registration_data(email="not-an-email"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newquestuser").exists())
        self.assertIn("email", response.context["form"].errors)

    def test_authenticated_user_is_redirected_from_registration(self):
        user = User.objects.create_user(username="signedin", password=STRONG_PASSWORD)
        self.client.force_login(user)
        response = self.client.get(reverse("register"))
        self.assertRedirects(response, reverse("account_home"))


class LoginViewTests(TestCase):
    """Day 3 login flow tests."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="loginuser",
            password=STRONG_PASSWORD,
            display_name="Login User",
        )

    def test_login_page_returns_200(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertContains(response, "Welcome Back")

    def test_valid_login_works(self):
        response = self.client.post(
            reverse("login"),
            {"username": "loginuser", "password": STRONG_PASSWORD},
        )
        self.assertRedirects(response, reverse("account_home"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_invalid_login_is_rejected(self):
        response = self.client.post(
            reverse("login"),
            {"username": "loginuser", "password": "WrongPassword2026!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertTrue(response.context["form"].non_field_errors())

    def test_invalid_login_does_not_reveal_account_existence(self):
        unknown_response = self.client.post(
            reverse("login"),
            {"username": "missinguser", "password": "WrongPassword2026!"},
        )
        known_response = self.client.post(
            reverse("login"),
            {"username": "loginuser", "password": "WrongPassword2026!"},
        )
        unknown_error = unknown_response.context["form"].non_field_errors()[0]
        known_error = known_response.context["form"].non_field_errors()[0]
        self.assertEqual(unknown_error, known_error)

    def test_authenticated_user_is_redirected_from_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("account_home"))

    def test_safe_next_url_is_used_after_login(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "loginuser",
                "password": STRONG_PASSWORD,
                "next": reverse("learning_paths"),
            },
        )
        self.assertRedirects(response, reverse("learning_paths"))

    def test_unsafe_next_url_is_ignored(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "loginuser",
                "password": STRONG_PASSWORD,
                "next": "https://evil.example.com/",
            },
        )
        self.assertRedirects(response, reverse("account_home"))


class LogoutViewTests(TestCase):
    """Day 3 logout flow tests."""

    def setUp(self):
        self.user = User.objects.create_user(username="logoutuser", password=STRONG_PASSWORD)
        self.client.force_login(self.user)

    def test_authenticated_user_can_logout_using_post(self):
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("home"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_shows_message(self):
        response = self.client.post(reverse("logout"), follow=True)
        self.assertContains(response, "You have been logged out.")

    def test_get_logout_is_not_allowed(self):
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)


class AccountHomeViewTests(TestCase):
    """Day 3 protected account page tests."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="accountuser",
            password=STRONG_PASSWORD,
            display_name="Account Explorer",
        )
        self.account_url = reverse("account_home")

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.get(self.account_url)
        expected = f"{reverse('login')}?next={self.account_url}"
        self.assertRedirects(response, expected)

    def test_authenticated_user_can_access_page(self):
        self.client.force_login(self.user)
        response = self.client.get(self.account_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/account_home.html")

    def test_user_information_is_displayed(self):
        self.client.force_login(self.user)
        response = self.client.get(self.account_url)
        self.assertContains(response, "Welcome, Account Explorer")
        self.assertContains(response, "accountuser")


class NavigationTests(TestCase):
    """Navigation links for Day 3 authentication."""

    def test_unauthenticated_navigation_links_work(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, f'href="{reverse("login")}"')
        self.assertContains(response, f'href="{reverse("register")}"')
        self.assertContains(response, f'href="{reverse("learning_paths")}"')
        self.assertNotContains(response, f'href="{reverse("account_home")}"')

    def test_authenticated_navigation_links_work(self):
        user = User.objects.create_user(username="navuser", password=STRONG_PASSWORD)
        self.client.force_login(user)
        response = self.client.get(reverse("home"))
        self.assertContains(response, f'href="{reverse("account_home")}"')
        self.assertContains(response, f'action="{reverse("logout")}"')
        self.assertContains(response, "Logout")
        self.assertNotContains(response, f'href="{reverse("login")}"')

    def test_learning_paths_link_returns_200(self):
        response = self.client.get(reverse("learning_paths"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "learning/paths_placeholder.html")

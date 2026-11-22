from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape

from apps.learning.models import LearningPath

from .missions import MISSION_DEFINITIONS, question_steps, session_key
from .scenarios import MISSION, MAX_SCORE, SCENARIOS

User = get_user_model()
SESSION_KEY = "phishing_mission_v1"


class PhishingChallengeTests(TestCase):
    """Day 7: server-validated Phishing Detective mission tests."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="phishdetective",
            password="CyberQuest2026!Secure",
            display_name="Dana Detective",
        )
        self.home_url = reverse("challenge_home")
        self.briefing_url = reverse("phishing_briefing")
        self.challenge_url = reverse("phishing_challenge")

    def login(self):
        self.client.force_login(self.user)

    def start(self):
        self.login()
        return self.client.post(self.challenge_url, {"action": "start"})

    def submit_current(self, answer=None):
        if answer is None:
            index = self.client.session[SESSION_KEY]["index"]
            answer = SCENARIOS[index]["answer"]
        return self.client.post(
            self.challenge_url,
            {"action": "submit", "answer": answer},
        )

    def advance(self):
        return self.client.post(self.challenge_url, {"action": "next"})

    def advance_to(self, index):
        for _ in range(index):
            self.submit_current()
            self.advance()

    def complete(self, answers=None):
        self.start()
        for position, scenario in enumerate(SCENARIOS):
            answer = answers[position] if answers else scenario["answer"]
            self.submit_current(answer)
            self.advance()

    def assert_scenario_content(self, index):
        scenario = SCENARIOS[index]
        response = self.client.get(self.challenge_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Scenario {index + 1} of 5")
        self.assertContains(response, scenario["sender_name"])
        self.assertContains(response, scenario["sender_email"])
        self.assertContains(response, scenario["subject"])
        self.assertContains(response, scenario["date"])
        for clue in scenario["clues"]:
            self.assertContains(response, clue["label"])
        if scenario["link_text"]:
            self.assertContains(response, scenario["link_text"])
        if scenario["link_destination"]:
            self.assertContains(response, scenario["link_destination"])
        if scenario["attachment"]:
            self.assertContains(response, scenario["attachment"])

    # --- Access and landing page -----------------------------------------
    def test_challenge_landing_page_requires_login(self):
        response = self.client.get(self.home_url)
        expected = f"{reverse('login')}?next={self.home_url}"
        self.assertRedirects(response, expected)

    def test_challenge_view_requires_login(self):
        response = self.client.get(self.challenge_url)
        expected = f"{reverse('login')}?next={self.challenge_url}"
        self.assertRedirects(response, expected)

    def test_challenge_hub_shows_all_four_missions(self):
        self.login()
        response = self.client.get(self.home_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "challenges/hub.html")
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
        self.assertNotContains(response, "Completed")
        self.assertContains(response, reverse("learning_paths"))

    def test_phishing_briefing_shows_mission_details(self):
        self.login()
        response = self.client.get(self.briefing_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "challenges/phishing_home.html")
        self.assertContains(response, MISSION["title"])
        self.assertContains(response, MISSION["number"])
        self.assertContains(response, MISSION["difficulty"])
        self.assertContains(response, "5 scenarios")
        self.assertContains(response, MISSION["estimated_time"])
        self.assertContains(response, "Start Mission")
        self.assertContains(response, f'action="{self.challenge_url}" method="post"')
        self.assertContains(response, reverse("challenge_home"))

    def test_authenticated_user_can_open_challenge(self):
        self.login()
        response = self.client.get(self.challenge_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "challenges/phishing_challenge.html")
        self.assertContains(response, "Scenario 1 of 5")
        self.assertContains(response, SCENARIOS[0]["subject"])
        self.assertContains(response, "Submit Answer")

    # --- Scenario content -------------------------------------------------
    def test_scenario_1_account_verification_content(self):
        self.start()
        self.assert_scenario_content(0)

    def test_scenario_2_delivery_notification_content(self):
        self.start()
        self.advance_to(1)
        self.assert_scenario_content(1)

    def test_scenario_3_course_announcement_content(self):
        self.start()
        self.advance_to(2)
        self.assert_scenario_content(2)

    def test_scenario_4_prize_notification_content(self):
        self.start()
        self.advance_to(3)
        self.assert_scenario_content(3)

    def test_scenario_5_password_reset_content(self):
        self.start()
        self.advance_to(4)
        self.assert_scenario_content(4)

    # --- Answer validation and scoring ------------------------------------
    def test_correct_answer_is_validated_and_scores_100(self):
        self.start()
        self.submit_current(SCENARIOS[0]["answer"])
        response = self.client.get(self.challenge_url)

        self.assertEqual(response.context["score"], 100)
        self.assertTrue(response.context["result"]["correct"])
        self.assertContains(response, "Correct classification")
        self.assertContains(response, SCENARIOS[0]["explanation"])
        self.assertContains(response, "Warning signs")

    def test_incorrect_answer_is_validated_and_scores_0(self):
        self.start()
        wrong_answer = "legitimate" if SCENARIOS[0]["answer"] == "phishing" else "phishing"
        self.submit_current(wrong_answer)
        response = self.client.get(self.challenge_url)

        self.assertEqual(response.context["score"], 0)
        self.assertFalse(response.context["result"]["correct"])
        self.assertContains(response, "Not quite")
        self.assertContains(response, "Phishing")
        self.assertContains(response, "Warning signs")

    def test_score_is_calculated_from_all_submitted_answers(self):
        answers = ["legitimate", "phishing", "legitimate", "legitimate", "legitimate"]
        self.complete(answers)
        response = self.client.get(self.challenge_url)

        self.assertEqual(response.context["score"], 300)
        self.assertEqual(response.context["correct_count"], 3)
        self.assertEqual(response.context["incorrect_count"], 2)
        self.assertEqual(response.context["max_score"], MAX_SCORE)

    def test_duplicate_submission_cannot_score_twice(self):
        self.start()
        first = self.submit_current(SCENARIOS[0]["answer"])
        second = self.submit_current(SCENARIOS[0]["answer"])
        response = self.client.get(self.challenge_url)

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 400)
        self.assertEqual(response.context["score"], 100)
        self.assertEqual(len(response.context["review"]), 5)
        self.assertEqual(self.client.session[SESSION_KEY]["answers"], {"0": {"answer": "phishing"}})

    def test_scenario_progression_requires_submission_then_advances(self):
        self.start()
        first = self.client.get(self.challenge_url)
        self.assertEqual(first.context["scenario_number"], 1)
        self.assertIsNone(first.context["result"])

        self.submit_current()
        answered = self.client.get(self.challenge_url)
        self.assertEqual(answered.context["scenario_number"], 1)
        self.assertIsNotNone(answered.context["result"])

        self.advance()
        advanced = self.client.get(self.challenge_url)
        self.assertEqual(advanced.context["scenario_number"], 2)
        self.assertIsNone(advanced.context["result"])

    def test_completion_screen_shows_final_results(self):
        self.complete()
        response = self.client.get(self.challenge_url)

        self.assertTrue(response.context["completed"])
        self.assertEqual(response.context["score"], 500)
        self.assertEqual(response.context["correct_count"], 5)
        self.assertEqual(response.context["incorrect_count"], 0)
        self.assertEqual(response.context["accuracy"], 100)
        self.assertContains(response, "Mission completed")
        self.assertContains(response, "Excellent! You are a Phishing Detective.")
        self.assertContains(response, "Review your answers")
        self.assertContains(response, "Restart Challenge")
        self.assertContains(response, reverse("learning_paths"))

    def test_restart_resets_the_current_session(self):
        self.complete()
        self.client.post(self.challenge_url, {"action": "restart"})
        response = self.client.get(self.challenge_url)

        state = self.client.session[SESSION_KEY]
        self.assertEqual(state["index"], 0)
        self.assertEqual(state["answers"], {})
        self.assertFalse(state["completed"])
        self.assertEqual(response.context["score"], 0)
        self.assertEqual(response.context["scenario_number"], 1)

    def test_start_action_resets_existing_progress(self):
        self.start()
        self.submit_current()
        self.advance()

        self.client.post(self.challenge_url, {"action": "start"})
        response = self.client.get(self.challenge_url)

        self.assertEqual(response.context["scenario_number"], 1)
        self.assertEqual(response.context["score"], 0)

    def test_invalid_submissions_are_rejected(self):
        self.login()

        self.assertEqual(self.client.post(self.challenge_url, {}).status_code, 400)
        self.assertEqual(
            self.client.post(self.challenge_url, {"action": "unknown"}).status_code,
            400,
        )
        self.assertEqual(
            self.client.post(
                self.challenge_url,
                {"action": "submit", "answer": "maybe"},
            ).status_code,
            400,
        )
        self.assertEqual(
            self.client.post(self.challenge_url, {"action": "next"}).status_code,
            400,
        )

    def test_submission_after_completion_is_rejected(self):
        self.complete()
        response = self.client.post(
            self.challenge_url,
            {"action": "submit", "answer": "phishing"},
        )
        self.assertEqual(response.status_code, 400)

    # --- Safety and regression checks -------------------------------------
    def test_simulated_links_are_plain_text_not_links(self):
        self.start()
        for index, scenario in enumerate(SCENARIOS):
            with self.subTest(scenario=scenario["id"]):
                if index:
                    self.submit_current()
                    self.advance()
                response = self.client.get(self.challenge_url)
                if scenario["link_destination"]:
                    self.assertContains(response, scenario["link_destination"])
                    self.assertNotContains(
                        response,
                        f'href="{scenario["link_destination"]}"',
                    )
                    self.assertNotContains(
                        response,
                        f'https://{scenario["link_destination"]}',
                    )
                    self.assertContains(response, "This text is not clickable")

    def test_learning_and_dashboard_pages_still_work(self):
        LearningPath.objects.create(
            title="Phishing Detective",
            slug="phishing-detective",
            description="Learn to recognize phishing messages.",
            is_published=True,
        )
        self.login()

        catalog = self.client.get(reverse("learning_paths"))
        detail = self.client.get(
            reverse("learning_path_detail", args=["phishing-detective"])
        )
        dashboard = self.client.get(reverse("dashboard"))

        self.assertEqual(catalog.status_code, 200)
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "Open Challenge")
        self.assertEqual(dashboard.status_code, 200)


class MissionFlowMixin:
    """Shared server-side flow tests for the Day 8-10 missions."""

    mission_slug = None

    def setUp(self):
        self.user = User.objects.create_user(
            username=f"{self.mission_slug.replace('-', '_')}_learner",
            password="CyberQuest2026!Secure",
            display_name="Mission Learner",
        )
        self.mission = MISSION_DEFINITIONS[self.mission_slug]
        self.name_prefix = self.mission_slug.replace("-", "_")
        self.landing_url = reverse(f"{self.name_prefix}_home")
        self.play_url = reverse(f"{self.name_prefix}_play")
        self.restart_url = reverse(f"{self.name_prefix}_restart")
        self.questions = question_steps(self.mission)

    def login(self):
        self.client.force_login(self.user)

    def state(self):
        return self.client.session.get(session_key(self.mission_slug), {})

    def start(self):
        self.login()
        return self.client.post(self.play_url, {"action": "start"})

    def current_step(self):
        return self.mission["steps"][self.state()["index"]]

    def submit_current(self, answer=None, correct=True):
        step = self.current_step()
        if answer is None:
            if correct:
                answer = step["answer"]
            else:
                answer = next(
                    choice["value"]
                    for choice in step["choices"]
                    if choice["value"] != step["answer"]
                )
        return self.client.post(
            self.play_url,
            {"action": "submit", "answer": answer},
        )

    def advance(self):
        return self.client.post(self.play_url, {"action": "next"})

    def go_to_step(self, index):
        self.start()
        for _ in range(index):
            if self.current_step()["kind"] == "question":
                self.submit_current()
            self.advance()

    def complete(self, wrong_slugs=()):
        self.start()
        for _ in range(len(self.mission["steps"]) + 2):
            state = self.state()
            if state.get("completed"):
                return
            step = self.mission["steps"][state["index"]]
            if step["kind"] == "question":
                self.submit_current(correct=step["slug"] not in wrong_slugs)
            self.advance()
        self.fail("Mission did not reach completion.")

    def test_anonymous_access_redirects_to_login(self):
        for url in (self.landing_url, self.play_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_landing_page_shows_briefing_and_start_action(self):
        self.login()
        response = self.client.get(self.landing_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "challenges/mission_home.html")
        self.assertContains(response, escape(self.mission["title"]))
        self.assertContains(response, escape(self.mission["number"]))
        self.assertContains(response, escape(self.mission["description"]))
        self.assertContains(response, escape(self.mission["difficulty"]))
        self.assertContains(response, escape(self.mission["estimated_time"]))
        for objective in self.mission["objectives"]:
            with self.subTest(objective=objective):
                self.assertContains(response, escape(objective))
        self.assertContains(response, f'action="{self.play_url}" method="post"')
        self.assertContains(response, "Start Mission")
        self.assertContains(response, str(self.mission["max_score"]))

    def test_start_action_creates_clean_state(self):
        self.start()
        while self.current_step()["kind"] == "activity":
            self.advance()
        self.submit_current()
        self.advance()

        self.client.post(self.play_url, {"action": "start"})
        state = self.state()
        self.assertEqual(state["index"], 0)
        self.assertEqual(state["answers"], {})
        self.assertFalse(state["completed"])

    def test_all_activities_render(self):
        for index, step in enumerate(self.mission["steps"]):
            if step["kind"] != "activity":
                continue
            with self.subTest(activity=step["slug"]):
                self.go_to_step(index)
                response = self.client.get(self.play_url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, escape(step["title"]))
                self.assertContains(response, escape(step["intro"]))
                self.assertTemplateUsed(response, step["template"])

    def test_question_content_is_hidden_until_submission(self):
        for index, step in enumerate(self.mission["steps"]):
            if step["kind"] != "question":
                continue
            with self.subTest(question=step["slug"]):
                self.go_to_step(index)
                response = self.client.get(self.play_url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, escape(step["title"]))
                self.assertContains(response, escape(step["prompt"][:45]))
                self.assertNotContains(response, "Correct answer:")
                self.assertNotContains(response, "Security tip")

    def test_correct_answer_is_validated_and_scores_100(self):
        first_question_index = next(
            index
            for index, step in enumerate(self.mission["steps"])
            if step["kind"] == "question"
        )
        self.go_to_step(first_question_index)
        self.submit_current()
        response = self.client.get(self.play_url)

        self.assertTrue(response.context["result"]["is_correct"])
        self.assertEqual(response.context["score"], 100)
        self.assertContains(response, "Correct answer")
        self.assertContains(response, escape(self.current_step()["explanation"]))

    def test_incorrect_answer_is_validated_and_scores_0(self):
        first_question_index = next(
            index
            for index, step in enumerate(self.mission["steps"])
            if step["kind"] == "question"
        )
        self.go_to_step(first_question_index)
        self.submit_current(correct=False)
        response = self.client.get(self.play_url)

        self.assertFalse(response.context["result"]["is_correct"])
        self.assertEqual(response.context["score"], 0)
        self.assertContains(response, "Not quite")
        self.assertContains(response, "Correct answer")

    def test_score_is_calculated_from_validated_answers(self):
        first_wrong = self.questions[0]["slug"]
        self.complete(wrong_slugs=[first_wrong])
        response = self.client.get(self.play_url)

        self.assertEqual(response.context["score"], self.mission["max_score"] - 100)
        self.assertEqual(response.context["correct_count"], len(self.questions) - 1)
        self.assertEqual(response.context["incorrect_count"], 1)
        self.assertEqual(response.context["accuracy"], round(((len(self.questions) - 1) / len(self.questions)) * 100))

    def test_duplicate_submission_cannot_score_twice(self):
        first_question_index = next(
            index
            for index, step in enumerate(self.mission["steps"])
            if step["kind"] == "question"
        )
        self.go_to_step(first_question_index)
        answer = self.current_step()["answer"]
        first = self.submit_current(answer=answer)
        second = self.submit_current(answer=answer)
        response = self.client.get(self.play_url)

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 400)
        self.assertEqual(response.context["score"], 100)
        self.assertEqual(len(self.state()["answers"]), 1)

    def test_next_requires_an_answer_for_question_steps(self):
        first_question_index = next(
            index
            for index, step in enumerate(self.mission["steps"])
            if step["kind"] == "question"
        )
        self.go_to_step(first_question_index)
        response = self.client.post(self.play_url, {"action": "next"})
        self.assertEqual(response.status_code, 400)

    def test_completion_screen_shows_final_results(self):
        self.complete()
        response = self.client.get(self.play_url)

        self.assertTrue(response.context["completed"])
        self.assertEqual(response.context["score"], self.mission["max_score"])
        self.assertEqual(response.context["correct_count"], len(self.questions))
        self.assertEqual(response.context["incorrect_count"], 0)
        self.assertEqual(response.context["accuracy"], 100)
        self.assertContains(response, "Mission completed")
        self.assertContains(response, escape(self.mission["performance"][len(self.questions)]))
        self.assertContains(response, "Review your answers")
        self.assertContains(response, "Restart Mission")
        self.assertContains(response, "Back to Challenges")
        self.assertContains(response, reverse("learning_paths"))

    def test_restart_url_resets_only_this_mission(self):
        self.complete()
        response = self.client.post(self.restart_url)

        self.assertRedirects(response, self.play_url)
        self.assertEqual(self.state(), {})
        page = self.client.get(self.play_url)
        self.assertEqual(page.context["score"], 0)
        self.assertEqual(page.context["step_number"], 1)
        self.assertFalse(page.context["completed"])

    def test_client_supplied_score_is_ignored(self):
        first_question_index = next(
            index
            for index, step in enumerate(self.mission["steps"])
            if step["kind"] == "question"
        )
        self.go_to_step(first_question_index)
        answer = self.current_step()["answer"]
        self.client.post(
            self.play_url,
            {"action": "submit", "answer": answer, "score": "999999"},
        )
        response = self.client.get(self.play_url)
        self.assertEqual(response.context["score"], 100)

    def test_invalid_submissions_are_rejected(self):
        self.start()
        cases = (
            {"action": "submit", "answer": "not-a-valid-answer"},
            {"action": "submit"},
            {"action": "unknown"},
            {},
        )
        for payload in cases:
            with self.subTest(payload=payload):
                response = self.client.post(self.play_url, payload)
                self.assertEqual(response.status_code, 400)

    def test_invalid_scenario_id_is_ignored(self):
        first_question_index = next(
            index
            for index, step in enumerate(self.mission["steps"])
            if step["kind"] == "question"
        )
        self.go_to_step(first_question_index)
        current_slug = self.current_step()["slug"]
        index_before = self.state()["index"]
        self.client.post(
            self.play_url,
            {
                "action": "submit",
                "answer": self.current_step()["answer"],
                "scenario_id": "999",
                "step": "999",
            },
        )
        state = self.state()
        self.assertEqual(state["index"], index_before)
        self.assertEqual(state["answers"], {current_slug: {"answer": self.mission["steps"][first_question_index]["answer"]}})


class PasswordGuardianTests(MissionFlowMixin, TestCase):
    mission_slug = "password-guardian"

    def test_password_strength_lab_is_local_only(self):
        self.go_to_step(0)
        response = self.client.get(self.play_url)

        self.assertContains(response, "Simulation only")
        self.assertContains(response, "Never enter a real password")
        self.assertContains(response, "Basic browser heuristic")
        self.assertContains(response, 'id="cq-password-input"')
        self.assertNotContains(response, 'name="password"')
        self.assertNotContains(response, 'name="cq-password-input"')

    def test_passphrase_builder_is_educational_and_ephemeral(self):
        self.go_to_step(1)
        response = self.client.get(self.play_url)

        self.assertContains(response, "Generate sample")
        self.assertContains(response, "Educational example only")
        self.assertContains(response, "Do not use generated samples")
        self.assertContains(response, "length and unpredictability")

    def test_password_reuse_scenario_explains_credential_stuffing(self):
        self.go_to_step(2)
        response = self.client.get(self.play_url)
        self.assertContains(response, "data breach")

        self.submit_current(answer="b")
        response = self.client.get(self.play_url)
        self.assertContains(response, "credential stuffing")
        self.assertContains(response, "unique password for every account")

    def test_mfa_scenario_explains_factors_and_passkeys(self):
        self.go_to_step(3)
        response = self.client.get(self.play_url)
        self.assertContains(response, "strong password")

        self.submit_current(answer="c")
        response = self.client.get(self.play_url)
        self.assertContains(response, "something you know")
        self.assertContains(response, "Passkeys and security keys")

    def test_quiz_feedback_is_explained_after_submission(self):
        expected = (
            (4, "b", "Unique passwords limit the damage"),
            (5, "a", "encrypts your passwords"),
            (6, "a", "another check beyond the password"),
        )
        for index, answer, fragment in expected:
            with self.subTest(index=index):
                self.go_to_step(index)
                self.submit_current(answer=answer)
                response = self.client.get(self.play_url)
                self.assertContains(response, escape(fragment))

    def test_typed_password_is_never_sent_to_server_or_session(self):
        self.go_to_step(2)
        secret = "NeverSendThisSample123!"
        self.client.post(
            self.play_url,
            {"action": "submit", "answer": "b", "password": secret},
        )
        self.assertNotIn(secret, str(self.client.session))

    def test_activity_javascript_uses_no_storage_or_network(self):
        js_path = Path(__file__).resolve().parents[2] / "static" / "js" / "challenges.js"
        content = js_path.read_text(encoding="utf-8")

        for forbidden in ("localStorage", "sessionStorage", "fetch(", "XMLHttpRequest"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, content)


class PrivacyProtectorTests(MissionFlowMixin, TestCase):
    mission_slug = "privacy-protector"

    def test_digital_footprint_profile_is_fictional_and_investigable(self):
        self.go_to_step(0)
        response = self.client.get(self.play_url)

        for fragment in (
            "Fictional profile",
            "Alex Learner",
            "Simulated City",
            "alex.learner@example.invalid",
            "Investigate Profile",
            "Identified risks",
            "Recommendations",
        ):
            with self.subTest(fragment=fragment):
                self.assertContains(response, fragment)

    def test_privacy_settings_panel_is_simulated(self):
        self.go_to_step(1)
        response = self.client.get(self.play_url)

        for fragment in (
            "Simulated panel only",
            "Profile visibility",
            "Location sharing",
            "Follower permissions",
            "Post visibility",
            "App permissions",
            "Review simulated settings",
        ):
            with self.subTest(fragment=fragment):
                self.assertContains(response, fragment)
        self.assertNotContains(response, 'name="cq-setting-visibility"')

    def test_privacy_decision_scenarios_have_explanations(self):
        expected = (
            (2, "b", "Location data can reveal"),
            (3, "b", "Photos can reveal locations"),
            (4, "b", "Only share information that is needed"),
        )
        for index, answer, fragment in expected:
            with self.subTest(index=index):
                self.go_to_step(index)
                self.submit_current(answer=answer)
                response = self.client.get(self.play_url)
                self.assertContains(response, escape(fragment))

    def test_privacy_quiz_feedback_is_explained(self):
        expected = (
            (5, "a", "become part of your digital footprint"),
            (6, "b", "Reviewing them helps keep access limited"),
            (7, "b", "reduce unnecessary exposure"),
        )
        for index, answer, fragment in expected:
            with self.subTest(index=index):
                self.go_to_step(index)
                self.submit_current(answer=answer)
                response = self.client.get(self.play_url)
                self.assertContains(response, escape(fragment))

    def test_privacy_completion_message(self):
        self.complete()
        response = self.client.get(self.play_url)
        self.assertContains(
            response,
            escape("Excellent! You understand how to protect your digital privacy."),
        )


class NetworkNavigatorTests(MissionFlowMixin, TestCase):
    mission_slug = "network-navigator"

    def test_network_diagram_explains_components_and_ip_addresses(self):
        self.go_to_step(0)
        response = self.client.get(self.play_url)

        for fragment in (
            "Device", "Wi-Fi", "Router", "Internet", "Server",
            "What is an IP address?", "simulated diagram",
        ):
            with self.subTest(fragment=fragment):
                self.assertContains(response, fragment)
        self.assertContains(response, "data-network-part")

    def test_wifi_investigator_uses_fictional_networks_only(self):
        self.go_to_step(1)
        response = self.client.get(self.play_url)

        for fragment in (
            "HomeNet", "Free_Public_WiFi", "SecureOffice", "Unknown_WiFi",
            "never scans real Wi-Fi", "network name is not proof of safety",
        ):
            with self.subTest(fragment=fragment):
                self.assertContains(response, fragment)
        self.assertNotContains(response, "navigator.mediaDevices")

    def test_network_fundamentals_identifies_router(self):
        self.go_to_step(2)
        response = self.client.get(self.play_url)
        self.assertContains(response, "forwards traffic")

        self.submit_current(answer="b")
        response = self.client.get(self.play_url)
        self.assertContains(response, "destination label")

    def test_safe_network_decisions_have_explanations(self):
        expected = (
            (3, "b", "Verify the network name, look for HTTPS"),
            (4, "b", "Anyone can create a network with a misleading name"),
            (5, "b", "Certificate warnings can indicate"),
        )
        for index, answer, fragment in expected:
            with self.subTest(index=index):
                self.go_to_step(index)
                self.submit_current(answer=answer)
                response = self.client.get(self.play_url)
                self.assertContains(response, escape(fragment))

    def test_network_quiz_feedback_is_explained(self):
        expected = (
            (6, "a", "Routers direct network traffic"),
            (7, "a", "Network names are labels, not proof of safety"),
            (8, "b", "Warnings are signals to pause and check"),
        )
        for index, answer, fragment in expected:
            with self.subTest(index=index):
                self.go_to_step(index)
                self.submit_current(answer=answer)
                response = self.client.get(self.play_url)
                self.assertContains(response, escape(fragment))

    def test_network_completion_message(self):
        self.complete()
        response = self.client.get(self.play_url)
        self.assertContains(
            response,
            escape("Excellent! You understand the fundamentals of network security."),
        )


class CommonMissionIntegrationTests(TestCase):
    """Cross-mission regression and integration checks."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="commonlearner",
            password="CyberQuest2026!Secure",
            display_name="Common Learner",
        )
        self.client.force_login(self.user)

    def test_each_mission_uses_an_isolated_session(self):
        for slug in MISSION_DEFINITIONS:
            url = reverse(f"{slug.replace('-', '_')}_play")
            self.client.post(url, {"action": "start"})

        for slug in MISSION_DEFINITIONS:
            with self.subTest(slug=slug):
                self.assertIn(session_key(slug), self.client.session)

        password_url = reverse("password_guardian_play")
        self.client.post(password_url, {"action": "next"})
        self.client.post(password_url, {"action": "next"})
        self.client.post(password_url, {"action": "submit", "answer": "b"})

        password_state = self.client.session[session_key("password-guardian")]
        privacy_state = self.client.session[session_key("privacy-protector")]
        network_state = self.client.session[session_key("network-navigator")]

        self.assertEqual(len(password_state["answers"]), 1)
        self.assertEqual(privacy_state["answers"], {})
        self.assertEqual(network_state["answers"], {})

    def test_invalid_mission_slug_returns_404(self):
        response = self.client.get("/challenges/not-a-real-mission/")
        self.assertEqual(response.status_code, 404)

    def test_restart_routes_reject_get_requests(self):
        for slug in MISSION_DEFINITIONS:
            with self.subTest(slug=slug):
                url = reverse(f"{slug.replace('-', '_')}_restart")
                self.assertEqual(self.client.get(url).status_code, 405)

    def test_learning_path_detail_links_to_each_new_mission(self):
        expected = {
            "password-guardian": "password_guardian_home",
            "privacy-protector": "privacy_protector_home",
            "network-navigator": "network_navigator_home",
        }
        for slug, url_name in expected.items():
            with self.subTest(slug=slug):
                LearningPath.objects.create(
                    title=slug.replace("-", " ").title(),
                    slug=slug,
                    description="Test path.",
                    is_published=True,
                )
                response = self.client.get(
                    reverse("learning_path_detail", args=[slug])
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, reverse(url_name))
                self.assertContains(response, "Open Challenge")

    def test_phishing_and_dashboard_remain_functional(self):
        phishing = self.client.get(reverse("phishing_challenge"))
        dashboard = self.client.get(reverse("dashboard"))

        self.assertEqual(phishing.status_code, 200)
        self.assertContains(phishing, "Scenario 1 of 5")
        self.assertEqual(dashboard.status_code, 200)
        self.assertContains(dashboard, reverse("challenge_home"))

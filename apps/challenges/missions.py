"""Data and session helpers for the Day 8-10 CyberQuest missions.

The engine is intentionally small and database-free. Each mission has its own
session key, its own exercises and its own performance messages. Activity
steps are educational only; only question steps contribute to the score.
"""

from django.urls import reverse

from .scenarios import MISSION as PHISHING_MISSION

SESSION_VERSION = 1


MISSION_DEFINITIONS = {
    "password-guardian": {
        "slug": "password-guardian",
        "title": "Password Guardian",
        "number": "Mission 02",
        "full_title": "Password Guardian — Mission 02",
        "subtitle": "Protect your digital identity with stronger password habits.",
        "description": (
            "Protect your digital identity. Learn to create stronger passwords, "
            "recognize risky password habits and defend accounts with "
            "multi-factor authentication."
        ),
        "difficulty": "Beginner",
        "estimated_time": "10–15 minutes",
        "icon": "key-round",
        "tone": "cyan",
        "landing_kicker": "Password security lab",
        "objectives": [
            "Explore password strength with a local-only simulation.",
            "Build a memorable passphrase from an educational word list.",
            "Recognize why password reuse enables credential stuffing.",
            "Explain how multi-factor authentication reduces account risk.",
        ],
        "total_questions": 5,
        "max_score": 500,
        "performance": {
            5: "Excellent! You understand the fundamentals of password security.",
            4: "Great job! You're building strong password habits.",
            3: "Good progress! Keep practicing your security skills.",
            2: "Keep learning! Review the password security lessons and try again.",
            1: "Keep learning! Review the password security lessons and try again.",
            0: "Keep learning! Review the password security lessons and try again.",
        },
        "steps": [
            {
                "kind": "activity",
                "slug": "password-strength-lab",
                "title": "Password Strength Lab",
                "eyebrow": "Interactive tool",
                "intro": (
                    "Try fictional sample passwords and watch the heuristic respond. "
                    "This tool runs entirely in your browser and is not a "
                    "professional password-strength engine."
                ),
                "template": "challenges/activities/password_strength.html",
            },
            {
                "kind": "activity",
                "slug": "passphrase-builder",
                "title": "Passphrase Builder",
                "eyebrow": "Interactive tool",
                "intro": (
                    "Generate a sample passphrase from a safe word list and see "
                    "why length and unpredictability make a difference."
                ),
                "template": "challenges/activities/passphrase_builder.html",
            },
            {
                "kind": "question",
                "slug": "password-reuse",
                "title": "Password Reuse Detective",
                "eyebrow": "Scenario",
                "prompt": (
                    "A student uses the same password for their email, social media "
                    "and gaming account. One of the websites suffers a data breach. "
                    "What could happen?"
                ),
                "choices": [
                    {"value": "a", "label": "A", "text": "Only the breached website is affected."},
                    {
                        "value": "b",
                        "label": "B",
                        "text": "Attackers might try the same password on other accounts.",
                    },
                    {"value": "c", "label": "C", "text": "Password reuse makes accounts more secure."},
                ],
                "answer": "b",
                "explanation": (
                    "Attackers often take passwords leaked from one breach and try "
                    "them on other websites. This is called credential stuffing. "
                    "Reusing a password means one breach can put several accounts "
                    "at risk."
                ),
                "tip": (
                    "Use a unique password for every account. A password manager can "
                    "generate and remember those passwords so you do not have to."
                ),
            },
            {
                "kind": "question",
                "slug": "mfa-defender",
                "title": "MFA Defender",
                "eyebrow": "Scenario",
                "prompt": (
                    "You have a strong password. Which additional security step "
                    "would help protect your account if someone obtains that password?"
                ),
                "choices": [
                    {
                        "value": "a",
                        "label": "A",
                        "text": "Reuse the password on fewer websites but keep it identical.",
                    },
                    {"value": "b", "label": "B", "text": "Disable security notifications."},
                    {"value": "c", "label": "C", "text": "Enable multi-factor authentication."},
                ],
                "answer": "c",
                "explanation": (
                    "Multi-factor authentication, or MFA, asks for more than one "
                    "kind of proof. That can be something you know, such as a "
                    "password; something you have, such as a phone or security "
                    "key; or something you are, such as a fingerprint. A stolen "
                    "password alone is usually not enough."
                ),
                "tip": (
                    "Passkeys and security keys can provide especially strong "
                    "protection because they resist phishing and reuse."
                ),
            },
            {
                "kind": "question",
                "slug": "password-quiz-1",
                "title": "Password Security Quiz · Question 1",
                "eyebrow": "Knowledge check",
                "prompt": "Which is generally the best password habit?",
                "choices": [
                    {"value": "a", "label": "A", "text": "Reuse one password everywhere."},
                    {"value": "b", "label": "B", "text": "Use unique passwords for each account."},
                    {"value": "c", "label": "C", "text": "Use your birth date."},
                ],
                "answer": "b",
                "explanation": (
                    "Unique passwords limit the damage of a breach. Personal "
                    "details such as birth dates are easy for attackers to guess "
                    "or find."
                ),
                "tip": "Let a password manager create and store unique passwords for you.",
            },
            {
                "kind": "question",
                "slug": "password-quiz-2",
                "title": "Password Security Quiz · Question 2",
                "eyebrow": "Knowledge check",
                "prompt": "What is a password manager used for?",
                "choices": [
                    {
                        "value": "a",
                        "label": "A",
                        "text": "To store and manage unique passwords securely.",
                    },
                    {"value": "b", "label": "B", "text": "To share passwords publicly."},
                    {"value": "c", "label": "C", "text": "To remove the need for account security."},
                ],
                "answer": "a",
                "explanation": (
                    "A reputable password manager encrypts your passwords and "
                    "helps you use a different one for every account. It supports, "
                    "rather than replaces, good account security."
                ),
                "tip": "Protect the password manager itself with MFA and a strong master passphrase.",
            },
            {
                "kind": "question",
                "slug": "password-quiz-3",
                "title": "Password Security Quiz · Question 3",
                "eyebrow": "Knowledge check",
                "prompt": "What does MFA add to account security?",
                "choices": [
                    {"value": "a", "label": "A", "text": "An additional verification factor."},
                    {"value": "b", "label": "B", "text": "A shorter password."},
                    {"value": "c", "label": "C", "text": "Automatic sharing of login credentials."},
                ],
                "answer": "a",
                "explanation": (
                    "MFA adds another check beyond the password, such as a code, "
                    "passkey, biometric check or security key."
                ),
                "tip": "Enable MFA wherever it is offered, especially on email and financial accounts.",
            },
        ],
    },
    "privacy-protector": {
        "slug": "privacy-protector",
        "title": "Privacy Protector",
        "number": "Mission 03",
        "full_title": "Privacy Protector — Mission 03",
        "subtitle": "Make smarter decisions about what you share online.",
        "description": (
            "Protect your personal information. Explore your digital footprint, "
            "understand privacy settings and make smarter decisions about what "
            "you share online."
        ),
        "difficulty": "Beginner",
        "estimated_time": "10–15 minutes",
        "icon": "eye-off",
        "tone": "purple",
        "landing_kicker": "Digital privacy lab",
        "objectives": [
            "Inspect a fictional profile for privacy risks.",
            "Practise adjusting simulated privacy settings.",
            "Evaluate location, sharing and data-request decisions.",
            "Explain digital footprints and thoughtful sharing.",
        ],
        "total_questions": 6,
        "max_score": 600,
        "performance": {
            6: "Excellent! You understand how to protect your digital privacy.",
            5: "Great job! You're making smarter privacy decisions.",
            4: "Good progress! Review your privacy protection habits.",
            3: "Good progress! Review your privacy protection habits.",
            2: "Keep learning! Practice protecting your personal information.",
            1: "Keep learning! Practice protecting your personal information.",
            0: "Keep learning! Practice protecting your personal information.",
        },
        "steps": [
            {
                "kind": "activity",
                "slug": "digital-footprint",
                "title": "Digital Footprint Investigator",
                "eyebrow": "Simulation",
                "intro": (
                    "Inspect the fictional profile of Alex. Select the clues, then "
                    "investigate the profile to reveal the risks."
                ),
                "template": "challenges/activities/digital_footprint.html",
            },
            {
                "kind": "activity",
                "slug": "privacy-settings",
                "title": "Privacy Settings Detective",
                "eyebrow": "Simulation",
                "intro": (
                    "Adjust the simulated settings and review the feedback. No "
                    "real account is connected to this panel."
                ),
                "template": "challenges/activities/privacy_settings.html",
            },
            {
                "kind": "question",
                "slug": "privacy-decision-1",
                "title": "Privacy Decision · Location Request",
                "eyebrow": "Scenario 1",
                "prompt": (
                    "A social media application requests access to your location "
                    "even though the application does not need location "
                    "information for its main function."
                ),
                "choices": [
                    {"value": "a", "label": "A", "text": "Grant location permission immediately."},
                    {
                        "value": "b",
                        "label": "B",
                        "text": "Review the permission and deny it if unnecessary.",
                    },
                    {"value": "c", "label": "C", "text": "Share your location publicly."},
                ],
                "answer": "b",
                "explanation": (
                    "Location data can reveal where you live, study or spend time. "
                    "If an app does not need it, denying the permission reduces "
                    "unnecessary sharing."
                ),
                "tip": "Review app permissions regularly and remove access you no longer need.",
            },
            {
                "kind": "question",
                "slug": "privacy-decision-2",
                "title": "Privacy Decision · Photo Sharing",
                "eyebrow": "Scenario 2",
                "prompt": (
                    "You are posting a photo of your school or workplace that "
                    "includes identifying information."
                ),
                "choices": [
                    {"value": "a", "label": "A", "text": "Post it publicly without checking."},
                    {
                        "value": "b",
                        "label": "B",
                        "text": "Review the image and privacy settings before sharing.",
                    },
                    {"value": "c", "label": "C", "text": "Share your personal details in the caption."},
                ],
                "answer": "b",
                "explanation": (
                    "Photos can reveal locations, routines and other people. "
                    "Checking the image and audience first helps you share "
                    "intentionally."
                ),
                "tip": "Crop identifying details and limit the audience when a post is personal.",
            },
            {
                "kind": "question",
                "slug": "privacy-decision-3",
                "title": "Privacy Decision · Unnecessary Data",
                "eyebrow": "Scenario 3",
                "prompt": (
                    "A website asks for unnecessary personal information to "
                    "access a simple service."
                ),
                "choices": [
                    {"value": "a", "label": "A", "text": "Provide everything requested."},
                    {
                        "value": "b",
                        "label": "B",
                        "text": "Review why the information is needed and avoid unnecessary sharing.",
                    },
                    {"value": "c", "label": "C", "text": "Share your account passwords."},
                ],
                "answer": "b",
                "explanation": (
                    "Only share information that is needed for the service. Never "
                    "give your account password to another website."
                ),
                "tip": "If a request feels excessive, look for an alternative service or ask why it is needed.",
            },
            {
                "kind": "question",
                "slug": "privacy-quiz-1",
                "title": "Privacy Quiz · Question 1",
                "eyebrow": "Knowledge check",
                "prompt": "What is a digital footprint?",
                "choices": [
                    {
                        "value": "a",
                        "label": "A",
                        "text": "The information and traces created through online activity.",
                    },
                    {"value": "b", "label": "B", "text": "A computer keyboard."},
                    {"value": "c", "label": "C", "text": "A security password."},
                ],
                "answer": "a",
                "explanation": (
                    "Posts, likes, comments, account details and even app "
                    "permissions can all become part of your digital footprint."
                ),
                "tip": "Pause before posting and ask whether you would be comfortable seeing it later.",
            },
            {
                "kind": "question",
                "slug": "privacy-quiz-2",
                "title": "Privacy Quiz · Question 2",
                "eyebrow": "Knowledge check",
                "prompt": "Why should you review application permissions?",
                "choices": [
                    {"value": "a", "label": "A", "text": "Applications always need access to everything."},
                    {
                        "value": "b",
                        "label": "B",
                        "text": "To limit unnecessary access to personal information and device features.",
                    },
                    {"value": "c", "label": "C", "text": "To make your data public."},
                ],
                "answer": "b",
                "explanation": (
                    "Permissions give apps access to data or device features. "
                    "Reviewing them helps keep access limited to what is actually "
                    "needed."
                ),
                "tip": "Check permissions after app updates because they can change.",
            },
            {
                "kind": "question",
                "slug": "privacy-quiz-3",
                "title": "Privacy Quiz · Question 3",
                "eyebrow": "Knowledge check",
                "prompt": "What is a safer social media privacy practice?",
                "choices": [
                    {"value": "a", "label": "A", "text": "Publicly share all personal information."},
                    {
                        "value": "b",
                        "label": "B",
                        "text": "Use privacy settings and share information thoughtfully.",
                    },
                    {"value": "c", "label": "C", "text": "Share account credentials with others."},
                ],
                "answer": "b",
                "explanation": (
                    "Privacy settings and thoughtful sharing reduce unnecessary "
                    "exposure. Account credentials should never be shared."
                ),
                "tip": "Revisit your privacy settings whenever a platform changes its options.",
            },
        ],
    },
    "network-navigator": {
        "slug": "network-navigator",
        "title": "Network Navigator",
        "number": "Mission 04",
        "full_title": "Network Navigator — Mission 04",
        "subtitle": "Explore the digital connections around you.",
        "description": (
            "Explore the digital connections around you. Understand network "
            "basics, recognize risky Wi-Fi connections and make safer network "
            "decisions."
        ),
        "difficulty": "Beginner",
        "estimated_time": "10–15 minutes",
        "icon": "network",
        "tone": "blue",
        "landing_kicker": "Network safety lab",
        "objectives": [
            "Identify common network components in a simulated diagram.",
            "Investigate fictional Wi-Fi networks without scanning real ones.",
            "Make safer decisions on public Wi-Fi and certificate warnings.",
            "Explain routers, network verification and cautious browsing.",
        ],
        "total_questions": 7,
        "max_score": 700,
        "performance": {
            7: "Excellent! You understand the fundamentals of network security.",
            6: "Great job! You're making safer network decisions.",
            5: "Good progress! Keep practicing network safety.",
            4: "Good progress! Keep practicing network safety.",
            3: "Keep learning! Review networking fundamentals and Wi-Fi security.",
            2: "Keep learning! Review networking fundamentals and Wi-Fi security.",
            1: "Keep learning! Review networking fundamentals and Wi-Fi security.",
            0: "Keep learning! Review networking fundamentals and Wi-Fi security.",
        },
        "steps": [
            {
                "kind": "activity",
                "slug": "network-fundamentals-diagram",
                "title": "Network Fundamentals",
                "eyebrow": "Interactive diagram",
                "intro": (
                    "Select each simulated component to learn what it does, then "
                    "answer the identification question."
                ),
                "template": "challenges/activities/network_diagram.html",
            },
            {
                "kind": "activity",
                "slug": "wifi-investigator",
                "title": "Wi-Fi Security Investigator",
                "eyebrow": "Simulation",
                "intro": (
                    "Inspect fictional networks and their security clues. No real "
                    "Wi-Fi is scanned and no connection is made."
                ),
                "template": "challenges/activities/wifi_investigator.html",
            },
            {
                "kind": "question",
                "slug": "network-fundamentals-identification",
                "title": "Network Fundamentals · Identification",
                "eyebrow": "Knowledge check",
                "prompt": (
                    "Which device commonly forwards traffic between your local "
                    "network and other networks?"
                ),
                "choices": [
                    {"value": "a", "label": "A", "text": "A web browser."},
                    {"value": "b", "label": "B", "text": "A router."},
                    {"value": "c", "label": "C", "text": "A text document."},
                ],
                "answer": "b",
                "explanation": (
                    "A router connects networks and forwards traffic toward its "
                    "destination, such as from your home network to the internet."
                ),
                "tip": "An IP address is like a destination label that helps devices route traffic.",
            },
            {
                "kind": "question",
                "slug": "network-decision-1",
                "title": "Safe Network Decision · Public Wi-Fi",
                "eyebrow": "Scenario 1",
                "prompt": (
                    "You are using public Wi-Fi at a café. The network has no "
                    "password and you need to access an account."
                ),
                "choices": [
                    {"value": "a", "label": "A", "text": "Connect and ignore all security concerns."},
                    {
                        "value": "b",
                        "label": "B",
                        "text": (
                            "Verify the network, use HTTPS and consider a trusted "
                            "alternative connection for sensitive activity."
                        ),
                    },
                    {"value": "c", "label": "C", "text": "Share your account password with the network administrator."},
                ],
                "answer": "b",
                "explanation": (
                    "Open networks may allow nearby attackers to observe or "
                    "interfere with traffic. Verify the network name, look for "
                    "HTTPS and avoid sensitive activity when the connection is not "
                    "trustworthy."
                ),
                "tip": "A VPN can help in some situations, but it does not guarantee complete security.",
            },
            {
                "kind": "question",
                "slug": "network-decision-2",
                "title": "Safe Network Decision · Similar Names",
                "eyebrow": "Scenario 2",
                "prompt": (
                    "You see two Wi-Fi networks with similar names. One is "
                    "verified by the venue and the other is unknown."
                ),
                "choices": [
                    {"value": "a", "label": "A", "text": "Connect to the unknown network immediately."},
                    {"value": "b", "label": "B", "text": "Verify the network with the venue before connecting."},
                    {"value": "c", "label": "C", "text": "Connect to both."},
                ],
                "answer": "b",
                "explanation": (
                    "Anyone can create a network with a misleading name. A fake "
                    "hotspot can try to trick people into connecting."
                ),
                "tip": "Ask staff for the exact network name instead of trusting the list alone.",
            },
            {
                "kind": "question",
                "slug": "network-decision-3",
                "title": "Safe Network Decision · Certificate Warning",
                "eyebrow": "Scenario 3",
                "prompt": (
                    "You receive a browser warning about a website's security "
                    "certificate."
                ),
                "choices": [
                    {"value": "a", "label": "A", "text": "Ignore the warning and enter sensitive information."},
                    {
                        "value": "b",
                        "label": "B",
                        "text": "Investigate the warning and avoid sensitive information until the issue is resolved.",
                    },
                    {"value": "c", "label": "C", "text": "Disable browser security permanently."},
                ],
                "answer": "b",
                "explanation": (
                    "Certificate warnings can indicate a configuration problem or "
                    "an attempt to intercept the connection. Do not enter "
                    "sensitive information until you understand the cause."
                ),
                "tip": "Keep browser security enabled so warnings can protect you.",
            },
            {
                "kind": "question",
                "slug": "network-quiz-1",
                "title": "Network Security Quiz · Question 1",
                "eyebrow": "Knowledge check",
                "prompt": "What does a router commonly do?",
                "choices": [
                    {"value": "a", "label": "A", "text": "Forward traffic between networks."},
                    {"value": "b", "label": "B", "text": "Store all passwords."},
                    {"value": "c", "label": "C", "text": "Automatically prevent every cyberattack."},
                ],
                "answer": "a",
                "explanation": (
                    "Routers direct network traffic. They are not password stores "
                    "and no single device prevents every cyberattack."
                ),
                "tip": "Good security uses several layers, not one magic device.",
            },
            {
                "kind": "question",
                "slug": "network-quiz-2",
                "title": "Network Security Quiz · Question 2",
                "eyebrow": "Knowledge check",
                "prompt": "Why should you verify public Wi-Fi network names?",
                "choices": [
                    {"value": "a", "label": "A", "text": "Anyone can create a network with a misleading name."},
                    {"value": "b", "label": "B", "text": "All public networks are safe."},
                    {"value": "c", "label": "C", "text": "Wi-Fi names guarantee encryption."},
                ],
                "answer": "a",
                "explanation": (
                    "Network names are labels, not proof of safety or encryption. "
                    "Verify the name with the venue before connecting."
                ),
                "tip": "Treat an unfamiliar or suspiciously familiar network with caution.",
            },
            {
                "kind": "question",
                "slug": "network-quiz-3",
                "title": "Network Security Quiz · Question 3",
                "eyebrow": "Knowledge check",
                "prompt": "What should you do when a website shows a security warning?",
                "choices": [
                    {"value": "a", "label": "A", "text": "Ignore the warning."},
                    {
                        "value": "b",
                        "label": "B",
                        "text": "Investigate and avoid sensitive activity until the issue is resolved.",
                    },
                    {"value": "c", "label": "C", "text": "Disable all security protections."},
                ],
                "answer": "b",
                "explanation": (
                    "Warnings are signals to pause and check. Disabling security "
                    "removes a useful protection rather than fixing the problem."
                ),
                "tip": "If you were expecting a secure connection, try again later or use a trusted network.",
            },
        ],
    },
}


MISSION_CARDS = [
    {
        "slug": "phishing-detective",
        "title": PHISHING_MISSION["title"],
        "number": PHISHING_MISSION["number"],
        "description": PHISHING_MISSION["description"],
        "difficulty": PHISHING_MISSION["difficulty"],
        "estimated_time": PHISHING_MISSION["estimated_time"],
        "icon": "mail-warning",
        "tone": "green",
        "url_name": "phishing_briefing",
    },
    {
        "slug": "password-guardian",
        "title": MISSION_DEFINITIONS["password-guardian"]["title"],
        "number": MISSION_DEFINITIONS["password-guardian"]["number"],
        "description": MISSION_DEFINITIONS["password-guardian"]["description"],
        "difficulty": MISSION_DEFINITIONS["password-guardian"]["difficulty"],
        "estimated_time": MISSION_DEFINITIONS["password-guardian"]["estimated_time"],
        "icon": MISSION_DEFINITIONS["password-guardian"]["icon"],
        "tone": MISSION_DEFINITIONS["password-guardian"]["tone"],
        "url_name": "password_guardian_home",
    },
    {
        "slug": "privacy-protector",
        "title": MISSION_DEFINITIONS["privacy-protector"]["title"],
        "number": MISSION_DEFINITIONS["privacy-protector"]["number"],
        "description": MISSION_DEFINITIONS["privacy-protector"]["description"],
        "difficulty": MISSION_DEFINITIONS["privacy-protector"]["difficulty"],
        "estimated_time": MISSION_DEFINITIONS["privacy-protector"]["estimated_time"],
        "icon": MISSION_DEFINITIONS["privacy-protector"]["icon"],
        "tone": MISSION_DEFINITIONS["privacy-protector"]["tone"],
        "url_name": "privacy_protector_home",
    },
    {
        "slug": "network-navigator",
        "title": MISSION_DEFINITIONS["network-navigator"]["title"],
        "number": MISSION_DEFINITIONS["network-navigator"]["number"],
        "description": MISSION_DEFINITIONS["network-navigator"]["description"],
        "difficulty": MISSION_DEFINITIONS["network-navigator"]["difficulty"],
        "estimated_time": MISSION_DEFINITIONS["network-navigator"]["estimated_time"],
        "icon": MISSION_DEFINITIONS["network-navigator"]["icon"],
        "tone": MISSION_DEFINITIONS["network-navigator"]["tone"],
        "url_name": "network_navigator_home",
    },
]


def get_mission(slug):
    """Return a mission definition or None for an unknown slug."""
    return MISSION_DEFINITIONS.get(slug)


def session_key(slug):
    """Return the isolated session key for a mission."""
    return f"cq_mission_{slug.replace('-', '_')}_v1"


def question_steps(mission):
    """Return only the scored question steps in order."""
    return [step for step in mission["steps"] if step["kind"] == "question"]


def choice_map(step):
    """Map answer values to their display labels and text."""
    return {choice["value"]: choice for choice in step.get("choices", [])}


def new_state():
    """Return a clean mission session state."""
    return {
        "version": SESSION_VERSION,
        "index": 0,
        "answers": {},
        "completed": False,
    }


def get_state(request, mission):
    """Read and sanitise mission state from the server-side session."""
    raw_state = request.session.get(session_key(mission["slug"]))
    if not isinstance(raw_state, dict) or raw_state.get("version") != SESSION_VERSION:
        return new_state()

    index = raw_state.get("index", 0)
    if (
        not isinstance(index, int)
        or isinstance(index, bool)
        or not 0 <= index < len(mission["steps"])
    ):
        return new_state()

    allowed = {
        step["slug"]: set(choice_map(step)) for step in question_steps(mission)
    }
    raw_answers = raw_state.get("answers", {})
    if not isinstance(raw_answers, dict):
        return new_state()

    answers = {}
    for key, value in raw_answers.items():
        if key not in allowed or not isinstance(value, dict):
            continue
        answer = value.get("answer")
        if answer in allowed[key]:
            answers[key] = {"answer": answer}

    completed = (
        bool(raw_state.get("completed", False))
        and len(answers) == len(allowed)
    )

    return {
        "version": SESSION_VERSION,
        "index": index,
        "answers": answers,
        "completed": completed,
    }


def save_state(request, mission, state):
    """Persist mission state in Django's server-side session."""
    request.session[session_key(mission["slug"])] = state


def reset_state(request, mission):
    """Clear mission progress from the session."""
    request.session.pop(session_key(mission["slug"]), None)


def score_for(mission, answers):
    """Recalculate score from validated answers and server-side answer keys."""
    score = 0
    correct = 0
    for step in question_steps(mission):
        selected = answers.get(step["slug"], {}).get("answer")
        if selected == step["answer"]:
            score += 100
            correct += 1
    return score, correct


def visible_step_for(step, result=None):
    """Return question data without revealing the answer key before submission."""
    base_keys = ("kind", "slug", "title", "eyebrow", "intro", "template", "prompt", "choices")
    visible = {key: step[key] for key in base_keys if key in step}
    if result is not None:
        visible["explanation"] = step["explanation"]
        visible["tip"] = step.get("tip", "")
    return visible


def build_context(request, mission, state):
    """Build all template data from validated server-side state."""
    score, correct_count = score_for(mission, state["answers"])
    questions = question_steps(mission)
    total_questions = len(questions)
    answered_count = len(state["answers"])
    incorrect_count = answered_count - correct_count
    accuracy = round((correct_count / total_questions) * 100)

    step = None
    result = None
    question_number = 0
    if not state["completed"]:
        step = mission["steps"][state["index"]]
        if step["kind"] == "question":
            for position, question in enumerate(questions, start=1):
                if question["slug"] == step["slug"]:
                    question_number = position
                    break
            selected = state["answers"].get(step["slug"], {}).get("answer")
            if selected:
                labels = choice_map(step)
                result = {
                    "is_correct": selected == step["answer"],
                    "selected_label": labels[selected]["label"],
                    "selected_text": labels[selected]["text"],
                    "correct_label": labels[step["answer"]]["label"],
                    "correct_text": labels[step["answer"]]["text"],
                    "explanation": step["explanation"],
                    "tip": step.get("tip", ""),
                }

    review = []
    for position, question in enumerate(questions, start=1):
        selected = state["answers"].get(question["slug"], {}).get("answer")
        labels = choice_map(question)
        review.append(
            {
                "number": position,
                "title": question["title"],
                "selected_label": labels[selected]["label"] if selected else "—",
                "selected_text": labels[selected]["text"] if selected else "Not answered",
                "correct_label": labels[question["answer"]]["label"],
                "correct_text": labels[question["answer"]]["text"],
                "is_correct": selected == question["answer"],
            }
        )

    progress_percent = (
        100
        if state["completed"]
        else round(((state["index"] + 1) / len(mission["steps"])) * 100)
    )
    slug = mission["slug"]

    return {
        "mission": mission,
        "mission_slug": slug,
        "hub_url": reverse("challenge_home"),
        "restart_url": reverse(f"{slug.replace('-', '_')}_restart"),
        "display_name": request.user.display_name or request.user.username,
        "step": visible_step_for(step, result) if step else None,
        "step_number": state["index"] + 1,
        "total_steps": len(mission["steps"]),
        "question_number": question_number,
        "total_questions": total_questions,
        "progress_percent": progress_percent,
        "score": score,
        "max_score": mission["max_score"],
        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
        "accuracy": accuracy,
        "performance_message": mission["performance"][correct_count],
        "result": result,
        "completed": state["completed"],
        "review": review,
    }

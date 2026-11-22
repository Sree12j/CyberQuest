"""Static, safe training data for the Phishing Detective mission.

All addresses use reserved example/invalid domains. Simulated links are displayed
as text only and are never rendered as clickable external URLs.
"""

MISSION = {
    "title": "Phishing Detective",
    "number": "Mission 01",
    "full_title": "Phishing Detective — Mission 01",
    "subtitle": "Investigate suspicious emails. Identify the threats. Protect yourself.",
    "description": (
        "Step into the role of a digital investigator. Examine five simulated "
        "emails, inspect the clues and decide whether each message is phishing "
        "or legitimate."
    ),
    "difficulty": "Beginner",
    "estimated_time": "10–15 minutes",
}

ANSWER_CHOICES = [
    ("phishing", "Phishing"),
    ("legitimate", "Legitimate"),
]

ANSWER_LABELS = dict(ANSWER_CHOICES)
VALID_ANSWERS = tuple(ANSWER_LABELS)

SCENARIOS = [
    {
        "id": "account-verification",
        "sender_name": "Account Security",
        "sender_email": "security@secure-account.example",
        "subject": "Urgent: Your account will be suspended",
        "date": "Today, 09:14 (simulated)",
        "body": (
            "Dear learner,\n\n"
            "We noticed unusual activity on your account. Your access will be "
            "suspended unless you verify your information immediately.\n\n"
            "To avoid interruption, confirm your details using the button below."
        ),
        "link_text": "Verify Your Account",
        "link_destination": "account-verification.example.invalid",
        "attachment": None,
        "answer": "phishing",
        "clues": [
            {
                "label": "Sender address",
                "detail": (
                    "The address uses secure-account.example, which is not a known "
                    "CyberQuest service domain."
                ),
                "icon": "at-sign",
            },
            {
                "label": "Urgent language",
                "detail": (
                    "The word Urgent and the suspension threat pressure you to act "
                    "before thinking carefully."
                ),
                "icon": "triangle-alert",
            },
            {
                "label": "Simulated link",
                "detail": (
                    "The button says Verify Your Account, but its displayed "
                    "destination is account-verification.example.invalid. It is text "
                    "only and cannot be opened."
                ),
                "icon": "link-2",
            },
            {
                "label": "Sensitive request",
                "detail": (
                    "The message asks you to verify account information through an "
                    "unfamiliar link."
                ),
                "icon": "lock-keyhole",
            },
        ],
        "explanation": (
            "This is phishing. The combination of an unfamiliar sender, urgent "
            "suspension threat and an unknown verification link is a classic "
            "account takeover attempt."
        ),
        "warning_signs": [
            "Unusual sender address",
            "Urgent language",
            "Threat of account suspension",
            "Verification requested through an unfamiliar link",
        ],
        "security_lesson": (
            "Open the official service independently by typing its known address "
            "in your browser instead of using a link from a message."
        ),
    },
    {
        "id": "delivery-notification",
        "sender_name": "Delivery Support",
        "sender_email": "delivery-update@parcel-notice.example",
        "subject": "Your parcel could not be delivered",
        "date": "Today, 11:38 (simulated)",
        "body": (
            "Hello,\n\n"
            "We could not deliver a parcel to your address. Pay a small delivery "
            "fee and confirm your personal details so we can try again.\n\n"
            "Use the option below to reschedule delivery."
        ),
        "link_text": "Reschedule Delivery",
        "link_destination": "parcel-payment.example.invalid",
        "attachment": "delivery-label.pdf (simulated — not downloadable)",
        "answer": "phishing",
        "clues": [
            {
                "label": "Unexpected delivery",
                "detail": (
                    "The message does not say which parcel or order it refers to."
                ),
                "icon": "package",
            },
            {
                "label": "Payment request",
                "detail": (
                    "A small unexpected fee is a common trick used to collect card "
                    "details."
                ),
                "icon": "credit-card",
            },
            {
                "label": "Simulated link",
                "detail": (
                    "The displayed destination is parcel-payment.example.invalid. "
                    "It is not clickable in this simulation."
                ),
                "icon": "link-2",
            },
            {
                "label": "Attachment",
                "detail": (
                    "A simulated delivery-label.pdf is shown for inspection only. "
                    "No file exists and nothing is downloaded."
                ),
                "icon": "paperclip",
            },
        ],
        "explanation": (
            "This is phishing. Unexpected delivery messages often use small fees, "
            "personal-data requests and attachments to create urgency."
        ),
        "warning_signs": [
            "Unexpected delivery notification",
            "Unusual payment request",
            "Suspicious simulated link",
            "Request for personal information",
        ],
        "security_lesson": (
            "Check deliveries through the retailer's or courier's official website "
            "using an order number you already trust."
        ),
    },
    {
        "id": "course-announcement",
        "sender_name": "Course Instructor",
        "sender_email": "instructor@campus.example",
        "subject": "Upcoming cybersecurity workshop",
        "date": "Yesterday, 15:05 (simulated)",
        "body": (
            "Hello everyone,\n\n"
            "This is a reminder that our beginner cybersecurity workshop takes "
            "place this Thursday. We will cover safe browsing, password habits "
            "and how to recognize suspicious messages.\n\n"
            "No action is required. See you in class."
        ),
        "link_text": None,
        "link_destination": None,
        "attachment": None,
        "answer": "legitimate",
        "clues": [
            {
                "label": "Expected sender",
                "detail": (
                    "The message comes from a course instructor at the simulated "
                    "campus.example address."
                ),
                "icon": "badge-check",
            },
            {
                "label": "Calm wording",
                "detail": (
                    "There is no urgency, threat or demand for immediate action."
                ),
                "icon": "message-square",
            },
            {
                "label": "No sensitive request",
                "detail": (
                    "The message does not ask for passwords, codes or payment "
                    "details."
                ),
                "icon": "shield-check",
            },
            {
                "label": "No links",
                "detail": (
                    "This simulated announcement contains no links or attachments."
                ),
                "icon": "link-2-off",
            },
        ],
        "explanation": (
            "This is a legitimate-style educational announcement. It matches the "
            "expected course context and asks only that students attend."
        ),
        "warning_signs": [],
        "security_lesson": (
            "Even expected messages deserve a quick check. If anything feels "
            "unusual, verify with the instructor through a known channel."
        ),
    },
    {
        "id": "prize-notification",
        "sender_name": "Rewards Team",
        "sender_email": "winner@rewards-claim.example",
        "subject": "Congratulations! You have won a gift card",
        "date": "Today, 13:02 (simulated)",
        "body": (
            "Congratulations!\n\n"
            "You have been selected to receive a gift card. To claim your prize, "
            "provide your full name, address and contact details using the form "
            "below.\n\n"
            "This offer is only available for a limited time."
        ),
        "link_text": "Claim Your Prize",
        "link_destination": "rewards-claim.example.invalid",
        "attachment": "prize-claim-form.pdf (simulated — not downloadable)",
        "answer": "phishing",
        "clues": [
            {
                "label": "Unexpected prize",
                "detail": (
                    "You did not enter a competition, so the promise is unlikely "
                    "to be real."
                ),
                "icon": "gift",
            },
            {
                "label": "Personal information",
                "detail": (
                    "The message asks for your full name, address and contact "
                    "details."
                ),
                "icon": "user-round",
            },
            {
                "label": "Suspicious sender",
                "detail": (
                    "The rewards-claim.example address is not connected to a known "
                    "service."
                ),
                "icon": "at-sign",
            },
            {
                "label": "Simulated link",
                "detail": (
                    "The displayed destination is rewards-claim.example.invalid. "
                    "It is plain text in this training scenario."
                ),
                "icon": "link-2",
            },
        ],
        "explanation": (
            "This is phishing. Unexpected prizes are frequently used to collect "
            "personal information or to encourage unsafe clicks."
        ),
        "warning_signs": [
            "Unexpected prize",
            "Request for personal information",
            "Suspicious sender",
            "Unrealistic promise",
        ],
        "security_lesson": (
            "Be skeptical of unexpected rewards. Never provide personal details to "
            "claim a prize you did not enter."
        ),
    },
    {
        "id": "password-reset-notice",
        "sender_name": "Security Notifications",
        "sender_email": "notifications@accounts.example",
        "subject": "Password reset request received",
        "date": "Today, 16:20 (simulated)",
        "body": (
            "Hello,\n\n"
            "A password reset request was received for your account. If you made "
            "this request, you can continue through the official application. If "
            "you did not, you can safely ignore this message.\n\n"
            "For your safety, do not reply with passwords or verification codes."
        ),
        "link_text": None,
        "link_destination": None,
        "attachment": None,
        "answer": "legitimate",
        "clues": [
            {
                "label": "Security notice",
                "detail": (
                    "Security notifications about reset requests can be legitimate."
                ),
                "icon": "bell-ring",
            },
            {
                "label": "No sensitive request",
                "detail": (
                    "The message does not ask you to send a password or code."
                ),
                "icon": "lock-keyhole",
            },
            {
                "label": "Independent verification",
                "detail": (
                    "It advises using the official application rather than a link "
                    "in the message."
                ),
                "icon": "shield-check",
            },
            {
                "label": "No links",
                "detail": (
                    "This simulated notice contains no clickable links or "
                    "attachments."
                ),
                "icon": "link-2-off",
            },
        ],
        "explanation": (
            "This is a legitimate-style security notification. It informs you, "
            "does not request sensitive data and encourages independent checking."
        ),
        "warning_signs": [],
        "security_lesson": (
            "Investigate unexpected reset notices calmly. Check your account "
            "through the official website or app and enable multifactor "
            "authentication where available."
        ),
    },
]

MAX_SCORE = len(SCENARIOS) * 100

PERFORMANCE_MESSAGES = {
    5: "Excellent! You are a Phishing Detective.",
    4: "Great work! You spotted most suspicious messages.",
    3: "Good progress! Review the warning signs.",
    2: "Keep learning! Practice identifying suspicious emails.",
    1: "Keep learning! Practice identifying suspicious emails.",
    0: "Keep learning! Practice identifying suspicious emails.",
}

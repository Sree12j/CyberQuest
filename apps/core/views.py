from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse

from apps.challenges.missions import MISSION_CARDS
from apps.learning.views import add_path_visuals, published_paths


def home(request):
    """Render the public CyberQuest homepage with real, published content."""
    all_paths = list(published_paths())
    missions = []
    for card in MISSION_CARDS:
        mission = dict(card)
        mission["url"] = reverse(card["url_name"])
        missions.append(mission)

    context = {
        "missions": missions,
        "featured_paths": add_path_visuals(all_paths[:3]),
        "total_paths": len(all_paths),
        "total_lessons": sum(path.lesson_count for path in all_paths),
    }
    return render(request, "core/home.html", context)


# Day 4 dashboard preview data.
# These dictionaries are static UI placeholders only. They are not connected to
# real XP, progress, achievements, challenges, leaderboards, or AI services.

DEMO_BADGES = [
    {
        "name": "First Quest",
        "description": "Complete your first learning step.",
        "icon": "sparkles",
        "earned": True,
    },
    {
        "name": "Phishing Detective",
        "description": "Spot suspicious email signals.",
        "icon": "mail-warning",
        "earned": True,
    },
    {
        "name": "Password Guardian",
        "description": "Master strong password habits.",
        "icon": "key-round",
        "earned": True,
    },
    {
        "name": "Privacy Protector",
        "description": "Protect your digital footprint.",
        "icon": "eye-off",
        "earned": False,
    },
    {
        "name": "Daily Explorer",
        "description": "Visit CyberQuest several days in a row.",
        "icon": "compass",
        "earned": False,
    },
    {
        "name": "Cyber Champion",
        "description": "Reach the highest preview tier.",
        "icon": "crown",
        "earned": False,
    },
]

DEMO_ACTIVITIES = [
    {
        "title": "Started Phishing Detective",
        "detail": "Learning path preview",
        "icon": "play-circle",
        "time": "Demo entry",
    },
    {
        "title": "Earned First Quest preview",
        "detail": "Achievement preview",
        "icon": "award",
        "time": "Demo entry",
    },
    {
        "title": "Completed a learning preview",
        "detail": "Password Guardian preview",
        "icon": "circle-check-big",
        "time": "Demo entry",
    },
]


@login_required
def dashboard(request):
    """Render the authenticated student dashboard."""
    display_name = request.user.display_name or request.user.username

    # Day 5: dashboard cards now use real published paths from the database.
    # Slicing here keeps the dashboard layout capped at six cards.
    dashboard_paths = add_path_visuals(list(published_paths()[:6]))

    context = {
        "dashboard_name": display_name,
        "demo_data_notice": (
            "Demonstration preview: XP, levels, streaks, badges, progress, "
            "challenges and AI replies are sample data only. Learning paths and "
            "lessons are real database content, but learner tracking is not implemented yet."
        ),
        "demo_stats": [
            {
                "label": "Total XP",
                "value": "1,250",
                "note": "Demo XP",
                "icon": "zap",
                "tone": "green",
            },
            {
                "label": "Level",
                "value": "4",
                "note": "60% to Level 5 · demo",
                "icon": "sparkles",
                "tone": "cyan",
                "progress": 60,
            },
            {
                "label": "Daily streak",
                "value": "7 days",
                "note": "Demo streak",
                "icon": "flame",
                "tone": "orange",
            },
            {
                "label": "Badges",
                "value": "6",
                "note": "Preview set",
                "icon": "award",
                "tone": "purple",
            },
        ],
        "learning_paths": dashboard_paths,
        "daily_quest": {
            "title": "Today's Cyber Quest",
            "challenge": "Learn to spot the warning signs of a suspicious email.",
            "description": (
                "A future interactive challenge will guide you through sender checks, "
                "link inspection and urgency clues. The challenge engine is not available yet."
            ),
            "reward": "+50 XP preview",
            "progress": "0 / 1 steps · demo",
            "icon": "target",
        },
        "progress_overview": {
            "percent": 42,
            "lessons_done": "12 of 30",
            "learning_time": "3h 20m",
            "current_activity": "Phishing Detective · preview",
        },
        "badges": DEMO_BADGES,
        "questmate_messages": [
            {
                "speaker": "You",
                "text": "What makes an email suspicious?",
                "tone": "user",
            },
            {
                "speaker": "QuestMate preview",
                "text": (
                    "Check the sender, hover over links, watch for urgency, and be careful "
                    "with unexpected attachments. This is a static example, not a live AI reply."
                ),
                "tone": "mentor",
            },
        ],
        "activities": DEMO_ACTIVITIES,
        "leaderboard": [
            {"rank": "1", "name": "Demo Learner 01", "points": "2,480 XP"},
            {"rank": "2", "name": "Demo Learner 02", "points": "1,960 XP"},
            {"rank": "3", "name": "Demo Learner 03", "points": "1,540 XP"},
        ],
    }
    return render(request, "core/dashboard.html", context)

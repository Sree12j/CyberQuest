from django.urls import path

from . import views

urlpatterns = [
    path("", views.challenge_home, name="challenge_home"),
    path(
        "phishing-detective/briefing/",
        views.phishing_briefing,
        name="phishing_briefing",
    ),
    path(
        "phishing-detective/restart/",
        views.phishing_restart,
        name="phishing_restart",
    ),
    path(
        "phishing-detective/",
        views.phishing_detective_challenge,
        name="phishing_challenge",
    ),
]

for slug in ("password-guardian", "privacy-protector", "network-navigator"):
    name_prefix = slug.replace("-", "_")
    urlpatterns += [
        path(
            f"{slug}/",
            views.mission_landing,
            {"slug": slug},
            name=f"{name_prefix}_home",
        ),
        path(
            f"{slug}/play/",
            views.mission_play,
            {"slug": slug},
            name=f"{name_prefix}_play",
        ),
        path(
            f"{slug}/restart/",
            views.mission_restart,
            {"slug": slug},
            name=f"{name_prefix}_restart",
        ),
    ]

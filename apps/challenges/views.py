from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .missions import (
    MISSION_CARDS,
    build_context as build_mission_context,
    choice_map,
    get_mission,
    get_state as get_mission_state,
    new_state as new_mission_state,
    question_steps,
    reset_state,
    save_state as save_mission_state,
)
from .scenarios import (
    ANSWER_LABELS,
    MAX_SCORE,
    MISSION,
    PERFORMANCE_MESSAGES,
    SCENARIOS,
    VALID_ANSWERS,
)

SESSION_KEY = "phishing_mission_v1"
SESSION_VERSION = 1
TOTAL_SCENARIOS = len(SCENARIOS)


# ---------------------------------------------------------------------------
# Day 7 Phishing Detective mission (preserved)
# ---------------------------------------------------------------------------


def new_state():
    """Return a clean phishing mission session state."""
    return {
        "version": SESSION_VERSION,
        "index": 0,
        "answers": {},
        "completed": False,
    }


def get_state(request):
    """Read a sanitised phishing mission state from the server-side session."""
    raw_state = request.session.get(SESSION_KEY)
    if not isinstance(raw_state, dict) or raw_state.get("version") != SESSION_VERSION:
        return new_state()

    index = raw_state.get("index", 0)
    if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < TOTAL_SCENARIOS:
        return new_state()

    raw_answers = raw_state.get("answers", {})
    if not isinstance(raw_answers, dict):
        return new_state()

    answers = {}
    for key, value in raw_answers.items():
        if not isinstance(key, str) or not key.isdigit():
            continue
        position = int(key)
        if not 0 <= position < TOTAL_SCENARIOS:
            continue
        if not isinstance(value, dict):
            continue
        answer = value.get("answer")
        if answer in VALID_ANSWERS:
            answers[key] = {"answer": answer}

    return {
        "version": SESSION_VERSION,
        "index": index,
        "answers": answers,
        "completed": bool(raw_state.get("completed", False)),
    }


def save_state(request, state):
    """Persist phishing mission state in Django's server-side session."""
    request.session[SESSION_KEY] = state


def score_for(answers):
    """Recalculate phishing score from answers and scenario data."""
    score = 0
    correct = 0
    for index, scenario in enumerate(SCENARIOS):
        selected = answers.get(str(index), {}).get("answer")
        if selected == scenario["answer"]:
            score += 100
            correct += 1
    return score, correct


def build_context(user, state):
    """Build all phishing template data from server-side state."""
    score, correct_count = score_for(state["answers"])
    answered_count = len(state["answers"])
    incorrect_count = answered_count - correct_count
    index = state["index"]
    completed = state["completed"]

    result = None
    scenario = None
    if not completed:
        scenario = SCENARIOS[index]
        selected = state["answers"].get(str(index), {}).get("answer")
        if selected:
            result = {
                "selected": selected,
                "selected_label": ANSWER_LABELS[selected],
                "correct": selected == scenario["answer"],
                "correct_label": ANSWER_LABELS[scenario["answer"]],
            }

    review = []
    for position, review_scenario in enumerate(SCENARIOS):
        selected = state["answers"].get(str(position), {}).get("answer")
        review.append(
            {
                "number": position + 1,
                "title": review_scenario["subject"],
                "selected_label": ANSWER_LABELS.get(selected, "Not answered"),
                "correct_label": ANSWER_LABELS[review_scenario["answer"]],
                "correct": selected == review_scenario["answer"],
            }
        )

    accuracy = round((correct_count / TOTAL_SCENARIOS) * 100)

    return {
        "mission": MISSION,
        "answer_choices": [
            {"value": value, "label": label} for value, label in ANSWER_LABELS.items()
        ],
        "display_name": user.display_name or user.username,
        "scenario": scenario,
        "scenario_number": index + 1,
        "total_scenarios": TOTAL_SCENARIOS,
        "progress_percent": 100 if completed else round(((index + 1) / TOTAL_SCENARIOS) * 100),
        "score": score,
        "max_score": MAX_SCORE,
        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
        "accuracy": accuracy,
        "performance_message": PERFORMANCE_MESSAGES[correct_count],
        "result": result,
        "completed": completed,
        "review": review,
    }


@login_required
def challenge_home(request):
    """Show the shared challenge hub with all available missions."""
    missions = []
    for card in MISSION_CARDS:
        mission_card = dict(card)
        mission_card["url"] = reverse(card["url_name"])
        missions.append(mission_card)
    return render(request, "challenges/hub.html", {"missions": missions})


@login_required
def phishing_briefing(request):
    """Show the Phishing Detective mission briefing."""
    return render(
        request,
        "challenges/phishing_home.html",
        {"mission": MISSION, "total_scenarios": TOTAL_SCENARIOS},
    )


@login_required
def phishing_detective_challenge(request):
    """Run the Phishing Detective mission with server-side scoring."""
    state = get_state(request)

    if request.method == "POST":
        action = request.POST.get("action", "")

        if action == "start":
            save_state(request, new_state())
            return redirect("phishing_challenge")

        if action == "restart":
            save_state(request, new_state())
            return redirect("phishing_challenge")

        if action == "submit":
            if state["completed"]:
                return HttpResponseBadRequest("Mission is already completed.")
            current_key = str(state["index"])
            if current_key in state["answers"]:
                return HttpResponseBadRequest("This scenario was already answered.")
            answer = request.POST.get("answer", "")
            if answer not in VALID_ANSWERS:
                return HttpResponseBadRequest("Invalid answer.")
            state["answers"][current_key] = {"answer": answer}
            save_state(request, state)
            return redirect("phishing_challenge")

        if action == "next":
            if state["completed"]:
                return HttpResponseBadRequest("Mission is already completed.")
            current_key = str(state["index"])
            if current_key not in state["answers"]:
                return HttpResponseBadRequest("Submit an answer before continuing.")
            if state["index"] == TOTAL_SCENARIOS - 1:
                state["completed"] = True
            else:
                state["index"] += 1
            save_state(request, state)
            return redirect("phishing_challenge")

        return HttpResponseBadRequest("Invalid challenge action.")

    return render(request, "challenges/phishing_challenge.html", build_context(request.user, state))


@login_required
@require_POST
def phishing_restart(request):
    """Reset only the Phishing Detective session."""
    request.session.pop(SESSION_KEY, None)
    return redirect("phishing_challenge")


# ---------------------------------------------------------------------------
# Day 8-10 reusable mission flow
# ---------------------------------------------------------------------------


def _mission_or_404(slug):
    mission = get_mission(slug)
    if mission is None:
        raise Http404("Unknown mission.")
    return mission


def _route_name(slug, suffix):
    return f"{slug.replace('-', '_')}_{suffix}"


@login_required
def mission_landing(request, slug):
    """Show a mission briefing for Password, Privacy or Network missions."""
    mission = _mission_or_404(slug)
    questions = question_steps(mission)
    return render(
        request,
        "challenges/mission_home.html",
        {
            "mission": mission,
            "start_url": reverse(_route_name(slug, "play")),
            "total_questions": len(questions),
            "activity_count": len(mission["steps"]) - len(questions),
            "max_score": mission["max_score"],
        },
    )


@login_required
def mission_play(request, slug):
    """Run a mission with server-validated answers and isolated session state."""
    mission = _mission_or_404(slug)
    state = get_mission_state(request, mission)

    if request.method == "POST":
        action = request.POST.get("action", "")

        if action in {"start", "restart"}:
            save_mission_state(request, mission, new_mission_state())
            return redirect(_route_name(slug, "play"))

        if state["completed"]:
            return HttpResponseBadRequest("Mission is already completed.")

        if action == "submit":
            step = mission["steps"][state["index"]]
            if step["kind"] != "question":
                return HttpResponseBadRequest("This exercise is not scored.")
            step_slug = step["slug"]
            if step_slug in state["answers"]:
                return HttpResponseBadRequest("This exercise was already answered.")
            answer = request.POST.get("answer", "")
            if answer not in choice_map(step):
                return HttpResponseBadRequest("Invalid answer.")
            state["answers"][step_slug] = {"answer": answer}
            save_mission_state(request, mission, state)
            return redirect(_route_name(slug, "play"))

        if action == "next":
            step = mission["steps"][state["index"]]
            if step["kind"] == "question" and step["slug"] not in state["answers"]:
                return HttpResponseBadRequest("Submit an answer before continuing.")
            if state["index"] == len(mission["steps"]) - 1:
                state["completed"] = True
            else:
                state["index"] += 1
            save_mission_state(request, mission, state)
            return redirect(_route_name(slug, "play"))

        return HttpResponseBadRequest("Invalid challenge action.")

    return render(
        request,
        "challenges/mission_play.html",
        build_mission_context(request, mission, state),
    )


@login_required
@require_POST
def mission_restart(request, slug):
    """Reset only the requested mission's session."""
    mission = _mission_or_404(slug)
    reset_state(request, mission)
    return redirect(_route_name(slug, "play"))

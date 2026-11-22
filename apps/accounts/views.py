from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, resolve_url
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CyberQuestAuthenticationForm, CyberQuestUserCreationForm


def _safe_next_url(request):
    """Return a safe redirect target after login."""
    next_url = request.POST.get("next") or request.GET.get("next")

    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url

    return resolve_url(settings.LOGIN_REDIRECT_URL)


def register(request):
    """Create a new CyberQuest account without logging the user in."""
    if request.user.is_authenticated:
        messages.info(request, "You are already signed in.")
        return redirect("account_home")

    if request.method == "POST":
        form = CyberQuestUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created. Please log in to continue.")
            return redirect("login")
    else:
        form = CyberQuestUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """Authenticate a user with Django's built-in authentication form."""
    if request.user.is_authenticated:
        messages.info(request, "You are already signed in.")
        return redirect("account_home")

    if request.method == "POST":
        form = CyberQuestAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            display_name = request.user.display_name or request.user.username
            messages.success(request, f"Welcome back, {display_name}!")
            return redirect(_safe_next_url(request))
    else:
        form = CyberQuestAuthenticationForm(request)

    context = {
        "form": form,
        "next": request.POST.get("next") or request.GET.get("next", ""),
    }
    return render(request, "accounts/login.html", context)


@require_POST
def logout_view(request):
    """End the session using a POST-only, CSRF-protected request."""
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


@login_required
def account_home(request):
    """Temporary authenticated-only account page."""
    account_name = request.user.display_name or request.user.username
    return render(
        request,
        "accounts/account_home.html",
        {"account_name": account_name},
    )

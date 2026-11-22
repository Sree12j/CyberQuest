from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class CyberQuestUserCreationForm(UserCreationForm):
    """Registration form built on Django's secure UserCreationForm."""

    display_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control cq-input",
                "placeholder": "How should we call you?",
                "autocomplete": "nickname",
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control cq-input",
                "placeholder": "you@example.com",
                "autocomplete": "email",
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("display_name", "username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control cq-input",
                "placeholder": "Choose a username",
                "autocomplete": "username",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control cq-input",
                "placeholder": "Create a strong password",
                "autocomplete": "new-password",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control cq-input",
                "placeholder": "Repeat your password",
                "autocomplete": "new-password",
            }
        )

    def clean_email(self):
        """Normalize the email before saving it."""
        return self.cleaned_data["email"].strip()

    def save(self, commit=True):
        """Save CyberQuest profile fields along with the hashed password."""
        user = super().save(commit=False)
        user.display_name = self.cleaned_data["display_name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

        return user


class CyberQuestAuthenticationForm(AuthenticationForm):
    """Login form with CyberQuest styling and a generic credential error."""

    error_messages = {
        "invalid_login": (
            "That username or password is not correct. Please try again."
        ),
        "inactive": "This account is inactive. Please contact support.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control cq-input",
                "placeholder": "Your username",
                "autocomplete": "username",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control cq-input",
                "placeholder": "Your password",
                "autocomplete": "current-password",
            }
        )

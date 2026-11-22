from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """CyberQuest user model with a small profile structure for future progress."""

    display_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional name shown elsewhere in CyberQuest.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["username"]
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.display_name or self.get_username()

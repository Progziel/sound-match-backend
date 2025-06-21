from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings


def validate_wav_url(url):
    """Ensure the provided sound file is a '.wav' file."""
    if not url.lower().endswith(".wav"):
        raise ValidationError("Only '.wav' files are allowed.")


def validate_sound_features(value):
    """Ensure sound_features contains exactly 5 elements"""
    if not isinstance(value, list) or len(value) != 5:
        raise ValidationError("Sound Features must be a list with exactly 5 elements.")


def validate_levels(value):
    """Ensure levels is a list of float values between 0 and 1"""
    if not isinstance(value, list):
        raise ValidationError("Levels must be a list.")
    if not all(isinstance(v, (float, int)) and 0 <= v <= 1 for v in value):
        raise ValidationError("All values in levels must "
                              "be floating-point numbers between 0 and 1.")


class Challenge(models.Model):
    id = models.AutoField(primary_key=True, blank=False, null=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_challenges",
        null=False, blank=False,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)
    sound_url = models.URLField(validators=[validate_wav_url], null=False, blank=False)
    sound_features = models.JSONField(validators=[validate_sound_features], null=False, blank=False)
    levels = models.JSONField(default=list, validators=[validate_levels], null=False, blank=False)
    invited_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="invited_challenges",
        blank=False
    )
    joined_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="joined_challenges",
        blank=False
    )

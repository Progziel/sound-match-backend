from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


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
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="created_challenges",
        null=False, blank=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)
    sound_url = models.URLField(null=False, blank=False)
    levels = models.JSONField(default=list, validators=[validate_levels],
                              null=False, blank=False)

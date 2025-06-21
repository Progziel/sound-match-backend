from django.db import models
from django.core.exceptions import ValidationError


def validate_wav_file(file):
    """Ensure uploaded file is a '.wav' file."""
    if not file.name.lower().endswith(".wav"):
        raise ValidationError("Only '.wav' sound files are allowed.")


class SoundPack(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    is_free = models.BooleanField(default=True, null=False, blank=False)
    price = models.DecimalField(
        max_digits=6, decimal_places=2, null=False, blank=False, default=0.0)
    created_at = models.DateTimeField(
        auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

    # SoundPack Cover Image
    pack_image = models.ImageField(
        upload_to="sound_packs/images/", null=True, blank=True)

    # Own Sounds (exactly 10) with images
    sound_1 = models.FileField(validators=[validate_wav_file],
        upload_to="sound_packs/sounds/", null=False, blank=False)
    sound_1_image = models.ImageField(
        upload_to="sound_packs/sounds_thumbnails/", null=True, blank=True)
    sound_2 = models.FileField(validators=[validate_wav_file],
        upload_to="sound_packs/sounds/", null=False, blank=False)
    sound_2_image = models.ImageField(
        upload_to="sound_packs/sounds_thumbnails/", null=True, blank=True)
    sound_3 = models.FileField(validators=[validate_wav_file],
        upload_to="sound_packs/sounds/", null=False, blank=False)
    sound_3_image = models.ImageField(
        upload_to="sound_packs/sounds_thumbnails/", null=True, blank=True)
    sound_4 = models.FileField(validators=[validate_wav_file],
        upload_to="sound_packs/sounds/", null=False, blank=False)
    sound_4_image = models.ImageField(
        upload_to="sound_packs/sounds_thumbnails/", null=True, blank=True)
    sound_5 = models.FileField(validators=[validate_wav_file],
        upload_to="sound_packs/sounds/", null=False, blank=False)
    sound_5_image = models.ImageField(
        upload_to="sound_packs/sounds_thumbnails/", null=True, blank=True)
    sound_6 = models.FileField(validators=[validate_wav_file],
        upload_to="sound_packs/sounds/", null=False, blank=False)
    sound_6_image = models.ImageField(
        upload_to="sound_packs/sounds_thumbnails/", null=True, blank=True)
    sound_7 = models.FileField(validators=[validate_wav_file],
        upload_to="sound_packs/sounds/", null=False, blank=False)
    sound_7_image = models.ImageField(
        upload_to="sound_packs/sounds_thumbnails/", null=True, blank=True)
    sound_8 = models.FileField(validators=[validate_wav_file],
        upload_to="sound_packs/sounds/", null=False, blank=False)
    sound_8_image = models.ImageField(
        upload_to="sound_packs/sounds_thumbnails/", null=True, blank=True)
    sound_9 = models.FileField(validators=[validate_wav_file],
        upload_to="sound_packs/sounds/", null=False, blank=False)
    sound_9_image = models.ImageField(
        upload_to="sound_packs/sounds_thumbnails/", null=True, blank=True)
    sound_10 = models.FileField(validators=[validate_wav_file],
        upload_to="sound_packs/sounds/", null=False, blank=False)
    sound_10_image = models.ImageField(
        upload_to="sound_packs/sounds_thumbnails/", null=True, blank=True)

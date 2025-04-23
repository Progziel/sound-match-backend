from django.conf import settings
from django.db import models


class Sound(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    file = models.FileField(upload_to='sounds/', null=False, blank=False)
    image = models.ImageField(upload_to='sounds_thumbnails/',
                              null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sounds"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True, null=False, blank=False)

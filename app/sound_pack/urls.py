"""URL mappings for the sound packs API."""
from django.urls import path
from .views import SoundPackViewSet, AdminSoundPackViewSet

app_name = "sound_pack"

urlpatterns = [
    # Regular users can only view sound packs
    path(
        "sound-packs/",
        SoundPackViewSet.as_view({"get": "list"}),
        name="sound-packs",
    ),
    path(
        "sound-packs/<int:pk>/",
        SoundPackViewSet.as_view({"get": "retrieve"}),
        name="sound-pack-detail",
    ),

    # Admin-only routes for managing sound packs
    path(
        "admin/sound-packs/",
        AdminSoundPackViewSet.as_view({"post": "create"}),
        name="admin-sound-packs",
    ),
    path(
        "admin/sound-packs/<int:pk>/",
        AdminSoundPackViewSet.as_view(
            {"patch": "partial_update", "delete": "destroy"}
        ),
        name="admin-sound-pack-detail",
    ),
]

"""Test SoundPack API"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import SoundPack
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from PIL import Image
import io

SOUNDPACK_LIST_URL = reverse("sound_pack:sound-packs")
ADMIN_SOUNDPACK_LIST_URL = reverse("sound_pack:admin-sound-packs")


def SOUNDPACK_DETAIL_URL(pk):
    return reverse("sound_pack:sound-pack-detail", args=[pk])


def ADMIN_SOUNDPACK_DETAIL_URL(pk):
    return reverse("sound_pack:admin-sound-pack-detail", args=[pk])


def create_admin_user(**params):
    """Create and return a new admin user"""
    return get_user_model().objects.create_superuser(**params)


def create_regular_user(**params):
    """Create and return a new regular user"""
    return get_user_model().objects.create_user(**params)


def create_soundpack(**params):
    """Create and return a new sound pack"""
    return SoundPack.objects.create(**params)


def payload(**params):
    """Generate a valid image for testing"""
    image = Image.new("RGB", (100, 100), color="red")
    image_io = io.BytesIO()
    image.save(image_io, format="PNG")
    image_io.seek(0)

    """Test Payload"""
    base_payload = {
        "name": "Test Pack",
        "is_free": False,
        "price": 9.99,
        "pack_image": SimpleUploadedFile("image.png", image_io.read(),
                                         content_type="image/png"),
        "sound_1": SimpleUploadedFile("sound1.wav", b"dummy sound"),
        "sound_2": SimpleUploadedFile("sound2.wav", b"dummy sound"),
        "sound_3": SimpleUploadedFile("sound3.wav", b"dummy sound"),
        "sound_4": SimpleUploadedFile("sound4.wav", b"dummy sound"),
        "sound_5": SimpleUploadedFile("sound5.wav", b"dummy sound"),
        "sound_6": SimpleUploadedFile("sound6.wav", b"dummy sound"),
        "sound_7": SimpleUploadedFile("sound7.wav", b"dummy sound"),
        "sound_8": SimpleUploadedFile("sound8.wav", b"dummy sound"),
        "sound_9": SimpleUploadedFile("sound9.wav", b"dummy sound"),
        "sound_10": SimpleUploadedFile("sound10.wav", b"dummy sound"),
    }
    base_payload.update(**params)
    return base_payload


class PublicSoundPackApiTests(TestCase):
    """Test unauthorized access restrictions for the SoundPack API"""

    def setUp(self):
        self.client = APIClient()

    def test_get_soundpack_list_unauthenticated(self):
        """Test unauthenticated users cannot access SoundPack list"""
        res = self.client.get(SOUNDPACK_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_single_soundpack_unauthenticated(self):
        """Test unauthenticated users cannot access a single SoundPack"""
        soundpack = create_soundpack(name="Single Pack", is_free=True)
        res = self.client.get(SOUNDPACK_DETAIL_URL(soundpack.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_soundpack_unauthenticated(self):
        """Test unauthenticated users cannot create SoundPacks"""
        pLoad = payload()
        res = self.client.post(SOUNDPACK_LIST_URL, pLoad, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_soundpack_unauthenticated(self):
        """Test unauthenticated users cannot update a SoundPack"""
        soundpack = create_soundpack(name="Test Pack", is_free=True)
        patch_payload = {"name": "Unauthorized Update"}
        res = self.client.patch(SOUNDPACK_DETAIL_URL(soundpack.id),
                                patch_payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_soundpack_unauthenticated(self):
        """Test unauthenticated users cannot delete SoundPacks"""
        soundpack = create_soundpack(name="Delete Test", is_free=False)
        res = self.client.delete(SOUNDPACK_DETAIL_URL(soundpack.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminSoundPackApiTests(TestCase):
    """Test admin-only access to modifying SoundPack API"""

    def setUp(self):
        self.admin_user = create_admin_user(
            email="admin@example.com", password="adminpass")
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

    def test_create_soundpack_admin(self):
        """Test admin can create a SoundPack"""
        pLoad = payload()
        res = self.client.post(
            ADMIN_SOUNDPACK_LIST_URL, pLoad, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_soundpack_admin(self):
        """Test admin can update an existing SoundPack"""
        soundpack = create_soundpack(name="Original Pack", is_free=True)
        patch_payload = {
            "name": "Updated Pack",
            "is_free": False,
            "price": "19.99",
        }
        res = self.client.patch(
            ADMIN_SOUNDPACK_DETAIL_URL(soundpack.id),
            patch_payload, format="json")
        soundpack.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(soundpack.name, "Updated Pack")
        self.assertEqual(soundpack.is_free, False)
        self.assertEqual(soundpack.price, Decimal("19.99"))

    def test_delete_soundpack_admin(self):
        """Test admin can delete SoundPacks"""
        soundpack = create_soundpack(name="Delete Test", is_free=False)
        res = self.client.delete(ADMIN_SOUNDPACK_DETAIL_URL(soundpack.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class PrivateUserSoundPackApiTests(TestCase):
    """Test private user restrictions on SoundPack API"""

    def setUp(self):
        self.user = create_regular_user(
            email="user@example.com", password="userpass")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_user_cannot_create_soundpack(self):
        """Test regular users cannot create a SoundPack"""
        pLoad = payload()
        res = self.client.post(SOUNDPACK_LIST_URL, pLoad, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_soundpack_private_user(self):
        """Test private users cannot update a SoundPack"""
        soundpack = create_soundpack(name="Test Pack", is_free=True)
        patch_payload = {"name": "Unauthorized Update"}
        res = self.client.patch(
            ADMIN_SOUNDPACK_DETAIL_URL(soundpack.id),
            patch_payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_delete_soundpack(self):
        """Test regular users cannot delete a SoundPack"""
        soundpack = create_soundpack(name="Delete Test", is_free=False)
        res = self.client.delete(SOUNDPACK_DETAIL_URL(soundpack.id))
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

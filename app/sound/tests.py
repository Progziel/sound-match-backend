"""Test Sound API"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models.sound import Sound
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

SOUND_LIST_URL = reverse('sound:sounds')
SOUND_CREATE_URL = reverse('sound:sounds')


def SOUND_DETAIL_URL(pk):
    """Return the URL for sound detail"""
    return reverse("sound:sound-detail", args=[pk])


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


def create_sound(user):
    """Create and return a new sound, ensuring `created_by` is set"""
    return Sound.objects.create(created_by=user, name="Test Sound",
                                file=SimpleUploadedFile(
                                    "sound.wav", b"dummy sound"))


def payload(**params):
    """Generate a valid image for testing"""
    image = Image.new("RGB", (100, 100), color="red")
    image_io = io.BytesIO()
    image.save(image_io, format="PNG")
    image_io.seek(0)

    """Test Payload"""
    base_payload = {
        "name": "Test Sound",
        "file": SimpleUploadedFile("sound.wav", b"dummy sound data"),
        "image": SimpleUploadedFile("image.png", image_io.read(),
                                    content_type="image/png")
    }
    base_payload.update(**params)
    return base_payload


class PublicSoundApiTests(TestCase):
    """Test the public features of the Sound API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required to access Sound API"""
        res = self.client.get(SOUND_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_sound_unauthenticated(self):
        """Test API rejects sound creation for unauthenticated users"""
        pLoad = payload()
        res = self.client.post(SOUND_CREATE_URL, pLoad, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_single_sound_unauthenticated(self):
        """Test API rejects unauthenticated sound retrieval"""
        dummy_sound_id = 0
        res = self.client.get(SOUND_DETAIL_URL(dummy_sound_id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_sound_unauthenticated(self):
        """Test API rejects unauthenticated sound deletion"""
        dummy_sound_id = 0
        res = self.client.delete(SOUND_DETAIL_URL(dummy_sound_id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateSoundApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(email="test@example.com",
                                password="testpass123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_sound_missing_fields(self):
        """Test API rejects sound creation with missing fields"""
        data = {"file": SimpleUploadedFile("test.wav", b"dummy sound data")}
        res = self.client.post(SOUND_CREATE_URL, data, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", res.json())

    def test_create_sound_authenticated(self):
        """Test creating a Sound as an authenticated user"""
        pLoad = payload()
        res = self.client.post(SOUND_CREATE_URL, pLoad, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_get_sound_list_authenticated(self):
        """Test retrieving all sounds for an authenticated user"""
        create_sound(user=self.user)
        create_sound(user=self.user)
        res = self.client.get(SOUND_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 2)

    def test_get_single_sound_authenticated(self):
        """Test retrieving a single Sound"""
        sound = create_sound(user=self.user)
        res = self.client.get(SOUND_DETAIL_URL(sound.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()["name"], "Test Sound")

    def test_delete_sound_authenticated(self):
        """Test deleting a Sound as an authenticated user"""
        sound = create_sound(user=self.user)
        res = self.client.delete(SOUND_DETAIL_URL(sound.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_cannot_delete_another_users_sound(self):
        """Test that a user cannot delete another user's sound"""
        other_user = create_user(email="otheruser@example.com",
                                 password="otherpass123")
        other_sound = create_sound(user=other_user)
        res = self.client.delete(SOUND_DETAIL_URL(other_sound.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

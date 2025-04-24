from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Challenge
from django.contrib.auth import get_user_model


CHALLENGE_LIST_URL = reverse("challenge:challenges")


def CHALLENGE_DETAIL_URL(pk):
    return reverse("challenge:challenge-detail", args=[pk])


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


def create_challenge(user, name="Dummy Challenge"):
    """Create and return a new challenge"""
    return Challenge.objects.create(
        created_by=user, name=name,
        sound_url="https://example.com/sounds/sound1.wav")


class PublicChallengeApiTests(TestCase):
    """Test unauthenticated access to the Challenge API"""

    def setUp(self):
        self.client = APIClient()

    def test_list_challenges_unauthenticated(self):
        """Test unauthenticated users cannot view challenge list"""
        res = self.client.get(CHALLENGE_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_challenge_unauthenticated(self):
        """Test unauthenticated users cannot create a challenge"""
        payload = {"name": "Unauthorized Challenge",
                   "sound_url": "https://example.com/sounds/sound1.wav"}
        res = self.client.post(CHALLENGE_LIST_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_challenge_by_id_unauthenticated(self):
        """Test unauthenticated users cannot retrieve a challenge by ID"""
        dummy_challenge_id = 0
        res = self.client.get(CHALLENGE_DETAIL_URL(dummy_challenge_id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_challenge_unauthenticated(self):
        """Test unauthenticated users cannot update a challenge"""
        payload = {"name": "Updated Challenge"}
        dummy_challenge_id = 0
        res = self.client.patch(CHALLENGE_DETAIL_URL(dummy_challenge_id),
                                payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateChallengeApiTests(TestCase):
    """Test authenticated access to the Challenge API"""

    def setUp(self):
        self.user = create_user(email="user@example.com", password="testpass")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_challenge_authenticated(self):
        """Test authenticated users can create a challenge"""
        payload = {
            "name": "New Challenge",
            "created_by": self.user.id,
            "sound_url": "https://example.com/sounds/sound1.wav",
            "levels": [0.10, 0.23, 0.35, 0.40]
        }
        res = self.client.post(CHALLENGE_LIST_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_patch_challenge_authenticated(self):
        """Test authenticated users can update a challenge"""
        challenge = create_challenge(user=self.user)
        payload = {"name": "Updated Challenge"}
        res = self.client.patch(CHALLENGE_DETAIL_URL(challenge.id),
                                payload, format="json")
        challenge.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(challenge.name, "Updated Challenge")

    def test_get_challenge_list_authenticated(self):
        """Test authenticated users can retrieve challenge list"""
        create_challenge(user=self.user)
        create_challenge(user=self.user)
        res = self.client.get(CHALLENGE_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreater(len(res.json()), 0)

    def test_get_challenge_by_id_authenticated(self):
        """Test authenticated users can retrieve a challenge by ID"""
        challenge = create_challenge(user=self.user, name="Test Challenge")
        res = self.client.get(CHALLENGE_DETAIL_URL(challenge.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()["name"], "Test Challenge")

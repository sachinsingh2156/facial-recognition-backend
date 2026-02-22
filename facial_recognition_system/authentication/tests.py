"""
Comprehensive tests for registration and authentication APIs.
Uses mocks for face_recognition so all branches are tested without real face images.
"""
from unittest.mock import patch, MagicMock
import numpy as np
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import User


# Placeholder for "valid" image in tests. We mock decode_base64_image to return a real array.
VALID_IMAGE_B64_PLACEHOLDER = "valid_image_b64_placeholder"


def _fake_decode_base64_image(base64_string):
    """Return a valid BGR image so view proceeds; used when we mock face_recognition."""
    if base64_string == VALID_IMAGE_B64_PLACEHOLDER:
        return np.zeros((100, 100, 3), dtype=np.uint8)
    return None


def _mock_face_encoding():
    return np.zeros(128, dtype=np.float64)


class RegisterAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/authentication/register/"

    def test_register_missing_face_image_returns_400(self):
        """Registration without face_image must return 400."""
        payload = {"unique_id": "u1", "name": "User One"}
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.json())
        self.assertIn("face_image", response.json()["message"].lower() or "")

    def test_register_invalid_image_data_returns_400(self):
        """Invalid base64/image data must return 400."""
        payload = {
            "unique_id": "u1",
            "name": "User One",
            "face_image": "not-valid-base64!!!",
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("Invalid", data["message"])

    @patch("authentication.views.decode_base64_image", _fake_decode_base64_image)
    @patch("authentication.views.face_recognition.face_locations")
    def test_register_no_face_in_image_returns_400(self, mock_face_locations):
        """When no face is detected, return 400 with 'No face found'."""
        mock_face_locations.return_value = []
        payload = {
            "unique_id": "u1",
            "name": "User One",
            "face_image": VALID_IMAGE_B64_PLACEHOLDER,
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No face found", response.json().get("message", ""))

    @patch("authentication.views.decode_base64_image", _fake_decode_base64_image)
    @patch("authentication.views.face_recognition.face_encodings")
    @patch("authentication.views.face_recognition.face_locations")
    def test_register_face_encoding_fails_returns_400(
        self, mock_face_locations, mock_face_encodings
    ):
        """When face encoding cannot be extracted, return 400."""
        mock_face_locations.return_value = [(10, 20, 30, 10)]
        mock_face_encodings.return_value = []
        payload = {
            "unique_id": "u1",
            "name": "User One",
            "face_image": VALID_IMAGE_B64_PLACEHOLDER,
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Could not extract face encoding", response.json().get("message", ""))

    @patch("authentication.views.decode_base64_image", _fake_decode_base64_image)
    @patch("authentication.views.face_recognition.face_distance")
    @patch("authentication.views.face_recognition.face_encodings")
    @patch("authentication.views.face_recognition.face_locations")
    @patch("authentication.views.imagehash.phash")
    def test_register_success_returns_201(
        self, mock_phash, mock_face_locations, mock_face_encodings, mock_face_distance
    ):
        """Valid new user registration returns 201."""
        mock_phash.return_value = MagicMock(__str__=lambda s: "hash1")
        mock_face_locations.return_value = [(10, 20, 30, 10)]
        mock_face_encodings.return_value = [_mock_face_encoding()]
        payload = {
            "unique_id": "user1",
            "name": "Alice",
            "face_image": VALID_IMAGE_B64_PLACEHOLDER,
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get("message"), "User registered successfully.")
        self.assertEqual(User.objects.count(), 1)
        u = User.objects.get(unique_id="user1")
        self.assertEqual(u.name, "Alice")

    @patch("authentication.views.decode_base64_image", _fake_decode_base64_image)
    @patch("authentication.views.face_recognition.face_distance")
    @patch("authentication.views.face_recognition.face_encodings")
    @patch("authentication.views.face_recognition.face_locations")
    @patch("authentication.views.imagehash.phash")
    def test_register_duplicate_image_same_hash_returns_400(
        self, mock_phash, mock_face_locations, mock_face_encodings, mock_face_distance
    ):
        """Same image (same perceptual hash) for different unique_id returns 400."""
        mock_phash.return_value = MagicMock(__str__=lambda s: "samehash")
        mock_face_locations.return_value = [(10, 20, 30, 10)]
        mock_face_encodings.return_value = [_mock_face_encoding()]
        User.objects.create(
            unique_id="existing",
            name="Existing",
            face_embedding=str(_mock_face_encoding().tolist()),
            image_hash="samehash",
        )
        payload = {
            "unique_id": "newid",
            "name": "New User",
            "face_image": VALID_IMAGE_B64_PLACEHOLDER,
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("exact image", data["message"].lower())
        self.assertIn("existing", data["message"])

    @patch("authentication.views.decode_base64_image", _fake_decode_base64_image)
    @patch("authentication.views.face_recognition.face_distance")
    @patch("authentication.views.face_recognition.face_encodings")
    @patch("authentication.views.face_recognition.face_locations")
    @patch("authentication.views.imagehash.phash")
    def test_register_same_face_different_photo_returns_400(
        self, mock_phash, mock_face_locations, mock_face_encodings, mock_face_distance
    ):
        """Same person (face match) registering with different photo under new ID returns 400."""
        mock_phash.return_value = MagicMock(__str__=lambda s: "differenthash")
        mock_face_locations.return_value = [(10, 20, 30, 10)]
        mock_face_encodings.return_value = [_mock_face_encoding()]
        mock_face_distance.return_value = np.array([0.35])
        User.objects.create(
            unique_id="member25",
            name="Member 25",
            face_embedding=str(_mock_face_encoding().tolist()),
            image_hash="hash25",
        )
        payload = {
            "unique_id": "member26",
            "name": "Member 26",
            "face_image": VALID_IMAGE_B64_PLACEHOLDER,
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("already registered", data["message"].lower())
        self.assertIn("member25", data["message"])
        self.assertEqual(User.objects.count(), 1)

    @patch("authentication.views.decode_base64_image", _fake_decode_base64_image)
    @patch("authentication.views.face_recognition.face_distance")
    @patch("authentication.views.face_recognition.face_encodings")
    @patch("authentication.views.face_recognition.face_locations")
    @patch("authentication.views.imagehash.phash")
    def test_register_duplicate_unique_id_returns_400(
        self, mock_phash, mock_face_locations, mock_face_encodings, mock_face_distance
    ):
        """Registering again with same unique_id returns 400 (IntegrityError)."""
        mock_phash.return_value = MagicMock(__str__=lambda s: "hash2")
        mock_face_locations.return_value = [(10, 20, 30, 10)]
        mock_face_encodings.return_value = [_mock_face_encoding()]
        mock_face_distance.return_value = np.array([0.5])
        User.objects.create(
            unique_id="dup",
            name="First",
            face_embedding=str(_mock_face_encoding().tolist()),
            image_hash="hash1",
        )
        payload = {
            "unique_id": "dup",
            "name": "Second",
            "face_image": VALID_IMAGE_B64_PLACEHOLDER,
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already exists", response.json().get("message", "").lower())


class AuthenticateAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.auth_url = "/api/authentication/authenticate/"

    def test_authenticate_missing_face_image_returns_400(self):
        """Authentication without face_image must return 400."""
        payload = {}
        response = self.client.post(self.auth_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("face_image", response.json().get("message", "").lower())

    def test_authenticate_invalid_image_returns_400(self):
        """Invalid image data must return 400."""
        payload = {"face_image": "invalid"}
        response = self.client.post(self.auth_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid", response.json().get("message", ""))

    @patch("authentication.views.decode_base64_image", _fake_decode_base64_image)
    @patch("authentication.views.face_recognition.face_locations")
    def test_authenticate_no_face_returns_400(self, mock_face_locations):
        """When no face in image, return 400."""
        mock_face_locations.return_value = []
        payload = {"face_image": VALID_IMAGE_B64_PLACEHOLDER}
        response = self.client.post(self.auth_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No face found", response.json().get("message", ""))

    @patch("authentication.views.decode_base64_image", _fake_decode_base64_image)
    @patch("authentication.views.face_recognition.face_encodings")
    @patch("authentication.views.face_recognition.face_locations")
    def test_authenticate_no_match_returns_401(
        self, mock_face_locations, mock_face_encodings
    ):
        """When no user matches (or no users), return 401."""
        mock_face_locations.return_value = [(10, 20, 30, 10)]
        mock_face_encodings.return_value = [_mock_face_encoding()]
        payload = {"face_image": VALID_IMAGE_B64_PLACEHOLDER}
        response = self.client.post(self.auth_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("No matching user found", response.json().get("message", ""))

    @patch("authentication.views.decode_base64_image", _fake_decode_base64_image)
    @patch("authentication.views.face_recognition.face_distance")
    @patch("authentication.views.face_recognition.face_encodings")
    @patch("authentication.views.face_recognition.face_locations")
    def test_authenticate_match_returns_200(
        self, mock_face_locations, mock_face_encodings, mock_face_distance
    ):
        """When a user matches within tolerance, return 200 with name and unique_id."""
        mock_face_locations.return_value = [(10, 20, 30, 10)]
        mock_face_encodings.return_value = [_mock_face_encoding()]
        mock_face_distance.return_value = np.array([0.3])
        User.objects.create(
            unique_id="member25",
            name="Member 25",
            face_embedding=str(_mock_face_encoding().tolist()),
            image_hash="h",
        )
        payload = {"face_image": VALID_IMAGE_B64_PLACEHOLDER}
        response = self.client.post(self.auth_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data.get("message"), "Authentication successful.")
        self.assertEqual(data.get("unique_id"), "member25")
        self.assertEqual(data.get("name"), "Member 25")

    @patch("authentication.views.decode_base64_image", _fake_decode_base64_image)
    @patch("authentication.views.face_recognition.face_distance")
    @patch("authentication.views.face_recognition.face_encodings")
    @patch("authentication.views.face_recognition.face_locations")
    def test_authenticate_different_person_above_tolerance_returns_401(
        self, mock_face_locations, mock_face_encodings, mock_face_distance
    ):
        """When probe is different person (distance > 0.4), return 401."""
        mock_face_locations.return_value = [(10, 20, 30, 10)]
        mock_face_encodings.return_value = [_mock_face_encoding()]
        mock_face_distance.return_value = np.array([0.6])
        User.objects.create(
            unique_id="member25",
            name="Member 25",
            face_embedding=str(_mock_face_encoding().tolist()),
            image_hash="h",
        )
        payload = {"face_image": VALID_IMAGE_B64_PLACEHOLDER}
        response = self.client.post(self.auth_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("No matching user found", response.json().get("message", ""))

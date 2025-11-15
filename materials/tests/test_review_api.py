"""
API tests for Review model
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from materials.models import Advertisement, Review

User = get_user_model()


class ReviewAPITest(TestCase):
    """Test Review API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create users
        self.user = User.objects.create_user(
            email="user@example.com", password="testpass123"
        )

        self.other_user = User.objects.create_user(
            email="other@example.com", password="testpass123"
        )

        # Create advertisement
        self.ad = Advertisement.objects.create(
            title="Test Product", price=1000, description="Test", author=self.user
        )

        # Create review
        self.review = Review.objects.create(
            text="Great product!", author=self.user, ad=self.ad
        )

    def test_list_reviews(self):
        """Test listing reviews"""
        url = reverse("materials:review-list-create")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_review_authenticated(self):
        """Test authenticated user can create review"""
        self.client.force_authenticate(user=self.other_user)

        url = reverse("materials:review-list-create")
        data = {"text": "Excellent!", "ad": self.ad.id}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 2)

    def test_create_review_anonymous_forbidden(self):
        """Test anonymous user cannot create review"""
        url = reverse("materials:review-list-create")
        data = {"text": "Test", "ad": self.ad.id}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_review_owner(self):
        """Test owner can update their review"""
        self.client.force_authenticate(user=self.user)

        url = reverse("materials:review-detail", args=[self.review.id])
        data = {"text": "Updated review text"}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.text, "Updated review text")

    def test_update_review_not_owner_forbidden(self):
        """Test non-owner cannot update review"""
        self.client.force_authenticate(user=self.other_user)

        url = reverse("materials:review-detail", args=[self.review.id])
        data = {"text": "Hacked"}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_owner(self):
        """Test owner can delete their review"""
        self.client.force_authenticate(user=self.user)

        url = reverse("materials:review-detail", args=[self.review.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)

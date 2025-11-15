"""
API tests for Advertisement model
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from materials.models import Advertisement

User = get_user_model()


class AdvertisementAPITest(TestCase):
    """Test Advertisement API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create users
        self.user = User.objects.create_user(
            email="user@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="adminpass123",
            first_name="Admin",
            last_name="User",
            role="admin",
        )

        # Create advertisements
        self.ad1 = Advertisement.objects.create(
            title="iPhone 15 Pro",
            price=50000,
            description="Новый iPhone",
            author=self.user,
        )

        self.ad2 = Advertisement.objects.create(
            title="MacBook Pro",
            price=80000,
            description="Новый MacBook",
            author=self.admin,
        )

    def test_list_advertisements_anonymous(self):
        """Test anonymous user can list advertisements"""
        url = reverse("materials:advertisement-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_list_advertisements_pagination(self):
        """Test pagination works (4 items per page)"""
        # Create 5 advertisements
        for i in range(3, 8):
            Advertisement.objects.create(
                title=f"Product {i}",
                price=i * 1000,
                description=f"Description {i}",
                author=self.user,
            )

        url = reverse("materials:advertisement-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)  # Page size = 4

    def test_retrieve_advertisement_detail(self):
        """Test retrieving advertisement detail"""
        url = reverse("materials:advertisement-detail", args=[self.ad1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "iPhone 15 Pro")
        self.assertEqual(response.data["price"], 50000)

    def test_create_advertisement_authenticated(self):
        """Test authenticated user can create advertisement"""
        self.client.force_authenticate(user=self.user)

        url = reverse("materials:advertisement-list")
        data = {"title": "iPad Pro", "price": 30000, "description": "Новый iPad Pro"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Advertisement.objects.count(), 3)
        self.assertEqual(response.data["author"], self.user.id)

    def test_create_advertisement_anonymous_forbidden(self):
        """Test anonymous user cannot create advertisement"""
        url = reverse("materials:advertisement-list")
        data = {"title": "Test Product", "price": 1000, "description": "Test"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_advertisement_owner(self):
        """Test owner can update their advertisement"""
        self.client.force_authenticate(user=self.user)

        url = reverse("materials:advertisement-detail", args=[self.ad1.id])
        data = {
            "title": "iPhone 15 Pro Updated",
            "price": 45000,
            "description": "Updated description",
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ad1.refresh_from_db()
        self.assertEqual(self.ad1.title, "iPhone 15 Pro Updated")
        self.assertEqual(self.ad1.price, 45000)

    def test_update_advertisement_not_owner_forbidden(self):
        """Test non-owner cannot update advertisement"""
        self.client.force_authenticate(user=self.user)

        url = reverse("materials:advertisement-detail", args=[self.ad2.id])
        data = {"title": "Hacked"}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_advertisement_admin_allowed(self):
        """Test admin can update any advertisement"""
        self.client.force_authenticate(user=self.admin)

        url = reverse("materials:advertisement-detail", args=[self.ad1.id])
        data = {"title": "Admin Updated"}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_advertisement_owner(self):
        """Test owner can delete their advertisement"""
        self.client.force_authenticate(user=self.user)

        url = reverse("materials:advertisement-detail", args=[self.ad1.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Advertisement.objects.count(), 1)

    def test_delete_advertisement_admin_allowed(self):
        """Test admin can delete any advertisement"""
        self.client.force_authenticate(user=self.admin)

        url = reverse("materials:advertisement-detail", args=[self.ad1.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_search_advertisements_by_title(self):
        """Test searching advertisements by title"""
        url = reverse("materials:advertisement-list")
        response = self.client.get(url, {"title": "iPhone"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "iPhone 15 Pro")

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from planetarium.models import AstronomyShow, ShowTheme

User = get_user_model()


class AstronomyShowViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@tt.com", password="password")
        self.client.force_authenticate(user=self.user)
        self.show_theme = ShowTheme.objects.create(name="Theme 1")
        self.astronomy_show = AstronomyShow.objects.create(
            title="Show 1", description="Description 1", show_theme=self.show_theme
        )
        self.astronomy_show_list_url = reverse("planetarium:astronomy_show-list")
        self.astronomy_show_detail_url = reverse(
            "planetarium:astronomy_show-detail", args=[self.astronomy_show.id]
        )

    def test_list_astronomy_shows(self):
        response = self.client.get(self.astronomy_show_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_astronomy_show(self):
        response = self.client.get(self.astronomy_show_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.astronomy_show.title)

    def test_admin_create_show_theme(self):
        staff_user = get_user_model().objects.create_user(
            email="staffuser@tt.com", password="password", is_staff=True
        )
        self.client.force_authenticate(user=staff_user)
        payload = {
            "title": "New Show",
            "description": "New Description",
            "show_theme": self.show_theme.id,
        }
        response = self.client.post(self.astronomy_show_list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AstronomyShow.objects.last().title, "New Show")
        response_data = response.data
        self.assertEqual(response_data["title"], "New Show")

    def test_admin_only_can_create_astronomy_show(self):
        payload = {
            "title": "New Show",
            "description": "New Description",
            "show_theme": self.show_theme.id,
        }
        response = self.client.post(self.astronomy_show_list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

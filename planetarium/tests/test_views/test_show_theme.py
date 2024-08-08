from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from planetarium.models import ShowTheme
from planetarium.serializers import ShowThemeSerializer

SHOW_THEME_URL = reverse("planetarium:show_theme-list")


class ShowThemeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_movie_list_auth_not_required(self):
        res = self.client.get(SHOW_THEME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_show_theme_list(self):
        ShowTheme.objects.create(name="Theme 1")
        ShowTheme.objects.create(name="Theme 2")
        response = self.client.get(SHOW_THEME_URL)
        show_themes = ShowTheme.objects.all()
        serializer = ShowThemeSerializer(show_themes, many=True)
        response_data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data["results"], serializer.data)

    def test_admin_create_show_theme(self):
        staff_user = get_user_model().objects.create_user(email='staffuser@tt.com', password='password', is_staff=True)
        self.client.force_authenticate(user=staff_user)
        payload = {"name": "New Theme"}
        response = self.client.post(SHOW_THEME_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ShowTheme.objects.count(), 1)
        self.assertEqual(ShowTheme.objects.last().name, 'New Theme')
        response_data = response.data
        self.assertEqual(response_data['name'], 'New Theme')

    def test_auth_user_cant_create_show_theme(self):
        auth_user = get_user_model().objects.create_user(email='staffuser@tt.com', password='password')
        self.client.force_authenticate(user=auth_user)
        payload = {"name": "New Theme"}
        response = self.client.post(SHOW_THEME_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_show_theme_detail(self):
        show_theme = ShowTheme.objects.create(name="Theme 1")
        url = reverse("planetarium:show_theme-detail", args=[show_theme.id])
        response = self.client.get(url)
        serializer = ShowThemeSerializer(show_theme)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

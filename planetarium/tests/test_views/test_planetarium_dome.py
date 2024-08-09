from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from planetarium.models import PlanetariumDome
from planetarium.serializers import PlanetariumDomeSerializer

PLANETARIUM_DOME_URL = reverse("planetarium:planetarium_dome-list")


class PlanetariumDomeViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.dome = PlanetariumDome.objects.create(
            name="Main Dome", rows=10, seats_in_row=15
        )

    def test_list_planetarium_domes(self):
        response = self.client.get(PLANETARIUM_DOME_URL)
        domes = PlanetariumDome.objects.all()
        serializer = PlanetariumDomeSerializer(domes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_admin_only_can_create_planetarium_dome(self):
        staff_user = get_user_model().objects.create(
            email="staff@tt.com", password="staffpassword", is_staff=True
        )
        self.client.force_authenticate(user=staff_user)
        payload = {"name": "Secondary Dome", "rows": 12, "seats_in_row": 20}
        response = self.client.post(PLANETARIUM_DOME_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PlanetariumDome.objects.count(), 2)
        self.assertEqual(PlanetariumDome.objects.last().name, "Secondary Dome")

    def test_not_admin_user_cannot_create_planetarium_dome(self):
        payload = {"name": "Anonymous Dome", "rows": 15, "seats_in_row": 25}
        response = self.client.post(PLANETARIUM_DOME_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_planetarium_dome_detail(self):
        url = reverse(
            "planetarium:planetarium_dome-detail", args=[self.dome.id]
        )
        response = self.client.get(url)
        serializer = PlanetariumDomeSerializer(self.dome)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_planetarium_domes_by_name(self):
        PlanetariumDome.objects.create(
            name="Secondary Dome", rows=15, seats_in_row=20
        )
        response = self.client.get(PLANETARIUM_DOME_URL, {"name": "Main"})
        domes = PlanetariumDome.objects.filter(name__icontains="Main")
        serializer = PlanetariumDomeSerializer(domes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from planetarium.models import ShowSession, AstronomyShow, PlanetariumDome, Ticket
from planetarium.serializers import ShowSessionsListSerializer, ShowSessionsRetrieveSerializer

User = get_user_model()
SHOW_SESSIONS_URL = reverse("planetarium:show_session-list")


class ShowSessionsViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="testuser@tt.com", password="password123")
        self.client.force_authenticate(user=self.user)
        self.astronomy_show = AstronomyShow.objects.create(title="Quasars2323")
        self.planetarium_dome = PlanetariumDome.objects.create(name="Dome 1", rows=10, seats_in_row=20)
        self.show_session = ShowSession.objects.create(
            astronomy_show=self.astronomy_show,
            planetarium_dome=self.planetarium_dome,
            show_time="2024-08-08 15:00"
        )

    def test_list_show_sessions(self):
        response = self.client.get(SHOW_SESSIONS_URL)
        show_sessions = ShowSession.objects.all()
        serializer = ShowSessionsListSerializer(show_sessions, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for res, ser in zip(response.data["results"], serializer.data):
            self.assertEqual(res["id"], ser["id"])
            self.assertEqual(res["astronomy_show"], ser["astronomy_show"])
            self.assertEqual(res["planetarium_dome"], ser["planetarium_dome"])
            self.assertEqual(res["show_time"], ser["show_time"])
            self.assertEqual(res["tickets_available"], 200)

    def test_anonymous_user_cant_create_show_session(self):
        payload = {
            "astronomy_show": self.astronomy_show.id,
            "planetarium_dome": self.planetarium_dome.id,
            "show_time": "2024-08-09 16:00"
        }
        response = self.client.post(SHOW_SESSIONS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_show_session_detail(self):
        url = reverse("planetarium:show_session-detail", args=[self.show_session.id])
        response = self.client.get(url)
        serializer = ShowSessionsRetrieveSerializer(self.show_session)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["id"], serializer.data["id"])
        self.assertEqual(response.data["astronomy_show"], serializer.data["astronomy_show"])
        self.assertEqual(response.data["planetarium_dome"], serializer.data["planetarium_dome"])
        self.assertEqual(response.data["show_time"], "2024-08-08, 15:00")
        self.assertEqual(response.data["tickets_available"], 200)

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from planetarium.models import Reservation
from planetarium.serializers import ReservationSerializer

User = get_user_model()
RESERVATION_URL = reverse("planetarium:reservation-list")


class ReservationViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="testuser@test.com", password="password123")
        self.client.force_authenticate(user=self.user)
        self.reservation = Reservation.objects.create(user=self.user)

    def test_list_reservations(self):
        response = self.client.get(RESERVATION_URL)
        reservations = Reservation.objects.filter(user=self.user)
        serializer = ReservationSerializer(reservations, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_create_reservation_for_auth_users(self):
        response = self.client.post(RESERVATION_URL)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 2)
        self.assertEqual(Reservation.objects.last().user, self.user)

    def test_anonymous_users_cant_create_reservation(self):
        client = APIClient()
        response = client.post(RESERVATION_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_reservation_detail(self):
        url = reverse("planetarium:reservation-detail", args=[self.reservation.id])
        response = self.client.get(url)
        serializer = ReservationSerializer(self.reservation)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

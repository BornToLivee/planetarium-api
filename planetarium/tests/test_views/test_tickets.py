from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from planetarium.models import Ticket, ShowSession, Reservation, AstronomyShow, PlanetariumDome
from django.contrib.auth import get_user_model

from planetarium.serializers import TicketRetrieveSerializer, TicketListSerializer

User = get_user_model()

SHOW_SESSIONS_URL = reverse("planetarium:show_session-list")
TICKETS_URL = reverse("planetarium:ticket-list")


class TicketViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="testuser@tt.com", password="password123")
        self.client.force_authenticate(user=self.user)

        self.astronomy_show = AstronomyShow.objects.create(title="Black Holes1")
        self.planetarium_dome = PlanetariumDome.objects.create(name="Dome 3", rows=10, seats_in_row=20)
        self.show_session = ShowSession.objects.create(
            astronomy_show=self.astronomy_show,
            planetarium_dome=self.planetarium_dome,
            show_time="2024-08-08 15:00"
        )
        self.reservation = Reservation.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            row=1,
            seat=1,
            show_session=self.show_session,
            reservation=self.reservation
        )

    def test_create_ticket_for_auth_user(self):
        payload = {
            "row": 2,
            "seat": 2,
            "show_session": self.show_session.id
        }
        response = self.client.post(TICKETS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 2)
        self.assertEqual(Ticket.objects.latest('id').row, 2)
        self.assertEqual(Ticket.objects.latest('id').seat, 2)
        self.assertEqual(Ticket.objects.latest('id').show_session, self.show_session)
        self.assertEqual(Ticket.objects.latest('id').reservation.user, self.user)

    def test_list_tickets(self):
        url = reverse("planetarium:ticket-list")
        response = self.client.get(url)
        tickets = Ticket.objects.filter(reservation__user=self.user)
        serializer = TicketListSerializer(tickets, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_get_ticket_detail(self):
        url = reverse("planetarium:ticket-detail", args=[self.ticket.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ticket_validation(self):
        payload = {
            "row": 15,
            "seat": 2,
            "show_session": self.show_session.id
        }
        response = self.client.post(TICKETS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_tickets_by_show_title(self):
        url = f"{reverse('planetarium:ticket-list')}?show_title={self.astronomy_show.title}"
        response = self.client.get(url)
        tickets = Ticket.objects.filter(
            reservation__user=self.user,
            show_session__astronomy_show__title__icontains=self.astronomy_show.title
        )
        serializer = TicketListSerializer(tickets, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

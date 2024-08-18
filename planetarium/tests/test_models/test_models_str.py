from django.contrib.auth import get_user_model
from django.test import TestCase

from planetarium.models import (
    AstronomyShow,
    PlanetariumDome,
    Reservation,
    ShowSession,
    ShowTheme,
    Ticket,
)

User = get_user_model()


class ModelStrTests(TestCase):
    def setUp(self):
        # Create a user for the Reservation model
        self.user = User.objects.create_user(
            email="testuser@tt.com", password="password123"
        )

        # Create instances for each model
        self.astronomy_show = AstronomyShow.objects.create(
            title="Galactic Wonders",
            description="An exploration of the universe's",
        )
        self.planetarium_dome = PlanetariumDome.objects.create(
            name="Main Dome", rows=10, seats_in_row=20
        )
        self.reservation = Reservation.objects.create(user=self.user)
        self.show_theme = ShowTheme.objects.create(name="Space Exploration")
        self.show_session = ShowSession.objects.create(
            astronomy_show=self.astronomy_show,
            planetarium_dome=self.planetarium_dome,
            show_time="2024-08-08 15:00",
        )
        self.ticket = Ticket.objects.create(
            row=1,
            seat=1,
            show_session=self.show_session,
            reservation=self.reservation
        )

    def test_astronomy_show_str(self):
        self.assertEqual(str(self.astronomy_show), "Galactic Wonders")

    def test_planetarium_dome_str(self):
        self.assertEqual(str(self.planetarium_dome), "Main Dome")

    def test_reservation_str(self):
        self.assertEqual(str(self.reservation), f"Reserved by {self.user}")

    def test_show_theme_str(self):
        self.assertEqual(str(self.show_theme), "Space Exploration")

    def test_show_session_str(self):
        self.assertEqual(
            str(self.show_session), "Galactic Wonders at 2024-08-08 15:00"
        )

    def test_ticket_str(self):
        self.assertEqual(
            str(self.ticket),
            "Row: 1, "
            "Seat: 1, ShowSession: "
            "Galactic Wonders at 2024-08-08 15:00",
        )

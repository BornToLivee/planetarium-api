from django.urls import include, path
from rest_framework import routers

from planetarium.views import (
    AstronomyShowViewSet,
    PlanetariumDomeViewSet,
    ReservationViewSet,
    ShowSessionsViewSet,
    ShowThemeViewSet,
    TicketViewSet,
)

router = routers.DefaultRouter()
router.register("show_themes", ShowThemeViewSet, basename="show_theme")
router.register("astronomy_shows", AstronomyShowViewSet, basename="astronomy_show")
router.register(
    "planetarium_domes", PlanetariumDomeViewSet, basename="planetarium_dome"
)
router.register("reservations", ReservationViewSet)
router.register("show_sessions", ShowSessionsViewSet, basename="show_session")
router.register("tickets", TicketViewSet, basename="ticket")

urlpatterns = [path("", include(router.urls))]

app_name = "planetarium"

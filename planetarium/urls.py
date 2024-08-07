from django.urls import path, include
from rest_framework import routers

from planetarium.views import (
    ShowThemeViewSet,
    AstronomyShowViewSet,
    PlanetariumDomeViewSet,
    ReservationViewSet,
    ShowSessionsViewSet,
    TicketViewSet,
)

router = routers.DefaultRouter()
router.register("show_themes", ShowThemeViewSet)
router.register("astronomy_shows", AstronomyShowViewSet, basename='astronomy_show')
router.register("planetarium_domes", PlanetariumDomeViewSet, basename='planetarium_dome')
router.register("reservations", ReservationViewSet)
router.register("show_sessions", ShowSessionsViewSet)
router.register("tickets", TicketViewSet, basename='ticket')

urlpatterns = [path("", include(router.urls))]

app_name = "planetarium"

from rest_framework import viewsets, mixins, status

from planetarium.models import (
    Reservation,
    ShowSession,
    Ticket,
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
)
from planetarium.serializers import (
    ReservationSerializer,
    ShowThemeSerializer,
    PlanetariumDomeSerializer,
    AstronomyShowListSerializer,
    ShowSessionsListSerializer,
    ShowSessionsRetrieveSerializer,
    TicketListSerializer,
    TicketRetrieveSerializer,
    TicketCreateSerializer, ShowSessionsCreateUpdateSerializer, AstronomyShowCreateUpdateSerializer,
    AstronomyShowRetrieveSerializer,
)


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.select_related("show_theme")

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        if self.action in ("create", "update"):
            return AstronomyShowCreateUpdateSerializer
        return AstronomyShowRetrieveSerializer


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related("user")
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ShowSessionsViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.select_related(
        "astronomy_show",
        "astronomy_show__show_theme",
        "planetarium_dome"
    )

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionsListSerializer
        if self.action in ("create", "update"):
            return ShowSessionsCreateUpdateSerializer
        return ShowSessionsRetrieveSerializer


class TicketViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        user = self.request.user
        return Ticket.objects.filter(reservation__user=user).select_related(
            "show_session__astronomy_show",
            "show_session__planetarium_dome",
            "reservation",
            "reservation__user",
        )


    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        if self.action == "create":
            return TicketCreateSerializer
        return TicketRetrieveSerializer

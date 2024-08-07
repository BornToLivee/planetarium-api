from django.db.models import F, Count
from rest_framework import viewsets, mixins, status

from planetarium.models import (
    Reservation,
    ShowSession,
    Ticket,
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
)
from planetarium.permissions import IsAdminOrReadOnly, IsAuthorized, IsAuthorizedOrReadOnly
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
    permission_classes = [IsAdminOrReadOnly]


class AstronomyShowViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = AstronomyShow.objects.select_related("show_theme")

        title = self.request.query_params.get("title")
        show_theme = self.request.query_params.get("show_theme")

        if title:
            queryset = queryset.filter(title__icontains=title)
        if show_theme:
            queryset = queryset.filter(show_theme__name__icontains=show_theme)
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        if self.action in ("create", "update"):
            return AstronomyShowCreateUpdateSerializer
        return AstronomyShowRetrieveSerializer


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    serializer_class = PlanetariumDomeSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = PlanetariumDome.objects.all()
        name = self.request.query_params.get("name")

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.distinct()


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related("user")
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthorized]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ShowSessionsViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.select_related(
        "astronomy_show",
        "astronomy_show__show_theme",
        "planetarium_dome"
    ).annotate(
        tickets_available=(F("planetarium_dome__rows") * F("planetarium_dome__seats_in_row") - Count("ticket"))
    )
    permission_classes = [IsAuthorizedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionsListSerializer
        if self.action in ("create", "update"):
            return ShowSessionsCreateUpdateSerializer
        return ShowSessionsRetrieveSerializer


class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorized]

    def get_queryset(self):
        user = self.request.user

        queryset = Ticket.objects.filter(reservation__user=user).select_related(
            "show_session__astronomy_show",
            "show_session__planetarium_dome",
            "reservation",
            "reservation__user",
        )

        show_title = self.request.query_params.get("show_title")

        if show_title:
            queryset = queryset.filter(show_session__astronomy_show__title__icontains=show_title)
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        if self.action == "create":
            return TicketCreateSerializer
        return TicketRetrieveSerializer

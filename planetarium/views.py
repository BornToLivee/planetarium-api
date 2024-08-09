from datetime import datetime

from django.db.models import F, Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

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
from planetarium.services.telegram_bot import send_telegram_message


class ShowThemeViewSet(viewsets.ModelViewSet):
    """Endpoints of the show themes in planetarium with basic CRUD operations"""
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer
    permission_classes = [IsAdminOrReadOnly]

    @method_decorator(cache_page(60 * 60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AstronomyShowViewSet(viewsets.ModelViewSet):
    """Endpoints of the astronomy shows in planetarium with basic CRUD operations"""
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type={"type": "list", "items": {"type": "string"}},
                description="Filter by title id (ex. ?title=title)",
            ),
            OpenApiParameter(
                "show_theme",
                type={"type": "list", "items": {"type": "string"}},
                description="Filter by show_theme (ex. ?show_theme=show_theme)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    """Endpoints of the planetarium domes description with basic CRUD operations"""
    serializer_class = PlanetariumDomeSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = PlanetariumDome.objects.all()
        name = self.request.query_params.get("name")

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.distinct()


class ReservationViewSet(viewsets.ModelViewSet):
    """Endpoints of the reservations in planetarium with basic CRUD operations"""
    queryset = Reservation.objects.select_related("user")
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthorized]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ShowSessionsViewSet(viewsets.ModelViewSet):
    """Endpoints of the show sessions in planetarium with basic CRUD operations"""
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

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[IsAuthorized],
    )
    def nearest_show(self, request):
        """Endpoint for searching nearest show in schedule"""
        now = datetime.now()
        nearest_session = self.queryset.filter(show_time__gte=now).order_by("show_time").first()

        if nearest_session:
            serializer = self.get_serializer(nearest_session)
            return Response(serializer.data)
        else:
            return Response({"detail": "No upcoming shows found."}, status=status.HTTP_404_NOT_FOUND)


class TicketViewSet(viewsets.ModelViewSet):
    """Endpoints of the tickets in planetarium with basic CRUD operations"""
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

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            ticket = Ticket.objects.get(id=response.data["id"])
            message = (
                f"New ticket created by {ticket.reservation.user.email}\n"
                f"Event: {ticket.show_session.astronomy_show.title}\n"
                f"Row: {ticket.row}, Seat: {ticket.seat}\n"
                f"Time: {ticket.show_session.show_time}"
            )
            send_telegram_message(message)
        return response

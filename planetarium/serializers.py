from rest_framework import serializers

from planetarium.models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    Reservation,
    ShowSession,
    Ticket,
)


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = ("id", "name")


class AstronomyShowListSerializer(serializers.ModelSerializer):
    show_theme = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="name"
    )

    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "show_theme")


class AstronomyShowRetrieveSerializer(AstronomyShowListSerializer):

    class Meta:
        model = AstronomyShow
        fields = AstronomyShowListSerializer.Meta.fields + ("description",)


class AstronomyShowCreateUpdateSerializer(AstronomyShowRetrieveSerializer):
    show_theme = serializers.PrimaryKeyRelatedField(
        queryset=ShowTheme.objects.all()
    )


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "rows", "seats_in_row", "capacity")


class PlanetariumDomeShowSessionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ("name", "capacity")


class ReservationSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = ("id", "user", "created_at")

    def get_created_at(self, obj):
        return obj.formatted_created_at


class ShowSessionsListSerializer(serializers.ModelSerializer):
    show_time = serializers.DateTimeField(format="%Y-%m-%d")
    astronomy_show = AstronomyShowListSerializer(read_only=False)
    planetarium_dome = PlanetariumDomeShowSessionsSerializer(read_only=False)

    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show", "planetarium_dome", "show_time")


class ShowSessionsRetrieveSerializer(ShowSessionsListSerializer):
    show_time = serializers.DateTimeField(format="%Y-%m-%d, %H:%M")
    astronomy_show = AstronomyShowRetrieveSerializer(read_only=False)
    planetarium_dome = PlanetariumDomeSerializer(read_only=False)


class ShowSessionsCreateUpdateSerializer(ShowSessionsListSerializer):
    astronomy_show = serializers.PrimaryKeyRelatedField(
        queryset=AstronomyShow.objects.all()
    )
    planetarium_dome = serializers.PrimaryKeyRelatedField(
        queryset=PlanetariumDome.objects.all()
    )


class ShowSessionTicketSerializer(serializers.ModelSerializer):
    show_title = serializers.SlugRelatedField(
        source="astronomy_show",
        many=False,
        read_only=True,
        slug_field="title",
    )
    planetarium_dome = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name",
    )

    class Meta:
        model = ShowSession
        fields = ("show_title", "planetarium_dome")


class TicketListSerializer(serializers.ModelSerializer):
    show_session = ShowSessionTicketSerializer(read_only=True)
    reservation = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="formatted_created_at"
    )

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "show_session", "reservation")


class TicketRetrieveSerializer(TicketListSerializer):
    show_session = ShowSessionsListSerializer(read_only=True)
    reservation = ReservationSerializer(read_only=True)


class TicketCreateSerializer(serializers.ModelSerializer):
    show_session = serializers.PrimaryKeyRelatedField(
        queryset=ShowSession.objects.all()
    )
    reservation = serializers.PrimaryKeyRelatedField(queryset=Reservation.objects.all())

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "show_session", "reservation")

    def create(self, validated_data):
        show_session = validated_data.pop("show_session")
        reservation = validated_data.pop("reservation")

        ticket = Ticket.objects.create(
            show_session=show_session, reservation=reservation, **validated_data
        )
        return ticket

    def update(self, instance, validated_data):
        show_session = validated_data.get("show_session")
        reservation = validated_data.get("reservation")

        if show_session is not None:
            instance.show_session = show_session
        if reservation is not None:
            instance.reservation = reservation

        instance.row = validated_data.get("row", instance.row)
        instance.seat = validated_data.get("seat", instance.seat)
        instance.save()

        return instance

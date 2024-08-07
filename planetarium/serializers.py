from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
        fields = ("id", "created_at")

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
    show_session = serializers.PrimaryKeyRelatedField(queryset=ShowSession.objects.all())

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "show_session")

    def validate(self, data):
        row = data['row']
        seat = data['seat']
        show_session = data['show_session']
        planetarium_dome = show_session.planetarium_dome

        if row < 1 or row > planetarium_dome.rows:
            raise ValidationError(f"Invalid row number. It must be between 1 and {planetarium_dome.rows}.")

        if seat < 1 or seat > planetarium_dome.seats_per_row:
            raise ValidationError(f"Invalid seat number. It must be between 1 and {planetarium_dome.seats_per_row}.")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        reservation = Reservation.objects.create(user=user)
        validated_data['reservation'] = reservation

        ticket = Ticket.objects.create(**validated_data)
        return ticket

    def update(self, instance, validated_data):
        show_session = validated_data.get("show_session")
        reservation = instance.reservation

        if show_session is not None:
            instance.show_session = show_session

        instance.row = validated_data.get("row", instance.row)
        instance.seat = validated_data.get("seat", instance.seat)
        instance.reservation = reservation
        instance.save()

        return instance

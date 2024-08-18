from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from planetarium_service import settings


class AstronomyShow(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    show_theme = models.ForeignKey(
        "ShowTheme", on_delete=models.DO_NOTHING, null=True, blank=True
    )

    def __str__(self):
        return self.title


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=200, unique=True)
    rows = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    seats_in_row = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    @property
    def formatted_created_at(self):
        return self.created_at.strftime("%Y-%m-%d, %H:%M:%S")

    def __str__(self):
        return f"Reserved by {self.user}"


class ShowTheme(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(AstronomyShow, on_delete=models.CASCADE)
    planetarium_dome = models.ForeignKey(
        PlanetariumDome,
        on_delete=models.CASCADE
    )
    show_time = models.DateTimeField()

    class Meta:
        ordering = ["-show_time"]

    def __str__(self):
        return f"{self.astronomy_show.title} at {self.show_time}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(ShowSession, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("show_session", "row", "seat")
        ordering = ["row", "seat"]

    def __str__(self):
        return (f"Row: {self.row}, Seat: {self.seat}, "
                f"ShowSession: {self.show_session}")

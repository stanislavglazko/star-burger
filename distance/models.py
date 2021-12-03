from django.db import models
from django.db.models.fields import FloatField


class PlaceCoords(models.Model):
    address = models.CharField(
        'Адрес места',
        unique=True,
        max_length=100,
    )
    date_of_calculate_coords = models.DateTimeField(
        'Дата получения координат места',
        null=True,
        blank=True,
        )
    lon = FloatField('Долгота')
    lat = FloatField('Широта')

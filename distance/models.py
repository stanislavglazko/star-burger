from django.db import models
from django.db.models.fields import FloatField
from django.utils import timezone


class PlaceCoords(models.Model):
    address = models.CharField(
        'Адрес места',
        unique=True,
        max_length=100,
    )
    date_of_calculate_coords = models.DateTimeField(
        'Дата получения координат места',
        auto_now=True,
        )
    lon = FloatField('Долгота', null=True, blank=True)
    lat = FloatField('Широта', null=True, blank=True)

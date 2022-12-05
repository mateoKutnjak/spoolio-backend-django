from django.core.validators import MinValueValidator
from django.db import models

from colorfield.fields import ColorField


class Color(models.Model):
    name = models.CharField(max_length=32)
    value = ColorField(default='#FF0000')

    def __str__(self) -> str:
        return "{} ({})".format(self.name, self.value)


class Material(models.Model):
    name = models.CharField(max_length=16)
    density = models.FloatField(validators=[MinValueValidator(0.0)])
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self) -> str:
        return "{} [{} g/cm3] price=${} per gram".format(self.name, self.density, self.price)
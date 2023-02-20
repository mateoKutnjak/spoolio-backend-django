from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from colorfield.fields import ColorField

from ...libs import models as libs_models


class Color(libs_models.SoftDeleteModel):
    name = models.CharField(max_length=32)
    value = ColorField(default='#FF0000')
    available = models.BooleanField()

    def __str__(self) -> str:
        return "{} ({})".format(self.name, self.value)


class Material(libs_models.SoftDeleteModel):
    name = models.CharField(max_length=16)
    description = models.CharField(max_length=256)
    density = models.FloatField(validators=[MinValueValidator(0.0)])
    price = models.DecimalField(max_digits=12, decimal_places=2)
    printing_speed = models.FloatField();
    available = models.BooleanField()

    def __str__(self) -> str:
        return "{} [{} g/cm3] price=${} per gram, v={} mm/s".format(self.name, self.density, self.price, self.printing_speed)


class Infill(libs_models.SoftDeleteModel):
    name = models.CharField(max_length=16)
    percentage = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    available = models.BooleanField()

    def __str__(self) -> str:
        return "{} - {}%".format(self.name, self.percentage * 100)
    

class Spool(libs_models.SoftDeleteModel):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    available = models.BooleanField()
    length = models.FloatField(validators=[MinValueValidator(0.0)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["material", "color"], 
                name='spool_material_color_unique_constraint')
        ]

    def __str__(self) -> str:
        return "{} {} - available length: {}".format(self.material.name, self.color.name, self.length)
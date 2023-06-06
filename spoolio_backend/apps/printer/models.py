from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from ..filament import models as filament_models

from ... libs import models as libs_models, storage_backends

    

class PrintingMethod(models.Model):

    name = models.CharField(max_length=16)
    full_name = models.CharField(max_length=128)
    
    resolution = models.PositiveSmallIntegerField(validators=[
                MinValueValidator(1),
                MaxValueValidator(5)
            ])
    precision = models.PositiveSmallIntegerField(validators=[
                MinValueValidator(1),
                MaxValueValidator(5)
            ])
    smoothness = models.PositiveSmallIntegerField(validators=[
                MinValueValidator(1),
                MaxValueValidator(5)
            ])
    pricing = models.PositiveSmallIntegerField(validators=[
                MinValueValidator(1),
                MaxValueValidator(5)
            ])

    supported_materials = models.ManyToManyField(filament_models.Material)

    def __str__(self) -> str:
        return "{} with supported materials = [{}]".format(self.name, ", ".join(str(m.name) for m in self.supported_materials.all()))


class PrinterType(libs_models.BaseTimestampModel):

    name = models.CharField(max_length=128)
    supported_materials = models.ManyToManyField(filament_models.Material)
    printing_method = models.ForeignKey(PrintingMethod, on_delete=models.CASCADE)

    picture = models.ImageField(storage=storage_backends.PublicMediaStorage(), upload_to='printer_type_pictures/', null=True, blank=True)

    max_print_size = models.CharField(max_length=128, help_text='Maximum print size dimenstions. Format: "x,y,z" in millimeters')
    max_resolution = models.FloatField(help_text='In millimeters')

    def __str__(self) -> str:
        return "{} (method={}) [{}]".format(self.name, self.printing_method, ", ".join(str(m.name) for m in self.supported_materials.all()))


class Printer(libs_models.BaseTimestampModel):

    name = models.CharField(max_length=128)
    type = models.ForeignKey(PrinterType, on_delete=models.CASCADE)
    available = models.BooleanField()

    def __str__(self) -> str:
        return "{}{} [{}]".format("NOT AVAILABLE: " if not self.available else '', self.name, self.type)
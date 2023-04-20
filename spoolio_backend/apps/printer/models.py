from django.db import models

from ..filament import models as filament_models

from ... libs import models as libs_models


class PrinterType(libs_models.BaseTimestampModel):

    name = models.CharField(max_length=128)
    supported_materials = models.ManyToManyField(filament_models.Material)

    def __str__(self) -> str:
        return "{} [{}]".format(self.name, ", ".join(str(m.name) for m in self.supported_materials.all()))


class Printer(libs_models.BaseTimestampModel):

    name = models.CharField(max_length=128)
    type = models.ForeignKey(PrinterType, on_delete=models.CASCADE)
    available = models.BooleanField()

    def __str__(self) -> str:
        return "{}{} [{}]".format("NOT AVAILABLE: " if not self.available else '', self.name, self.type)
    

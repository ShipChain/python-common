from enumfields import Enum, EnumIntegerField
from django.db import models
from shipchain_common import utils


class GenericEnum(Enum):
    FIRST = 0
    SECOND = 1
    THIRD = 2

    class Labels:
        FIRST = 'FIRST'
        SECOND = 'SECOND'
        THIRD = 'THIRD'


class EnumObject(models.Model):
    enum_field = EnumIntegerField(enum=GenericEnum, default=GenericEnum.FIRST)


class BasicModel(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=utils.random_id)
    my_field = models.CharField(max_length=1)

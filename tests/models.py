from enumfields import Enum, EnumIntegerField
from django.db.models import Model


class GenericEnum(Enum):
    FIRST = 0
    SECOND = 1
    THIRD = 2

    class Labels:
        FIRST = 'FIRST'
        SECOND = 'SECOND'
        THIRD = 'THIRD'


class EnumObject(Model):
    enum_field = EnumIntegerField(enum=GenericEnum, default=GenericEnum.FIRST)

    class Meta:
        app_label = 'tests'

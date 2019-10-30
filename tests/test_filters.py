import pytest
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from src.shipchain_common.filters import filter_enum
from tests.django_mocking.models import EnumObject, GenericEnum


@pytest.mark.django_db
class EnumObjectModel(TestCase):
    def test_enum_filter(self):
        EnumObject.objects.create(enum_field=GenericEnum.FIRST)
        assert filter_enum(EnumObject.objects.all(), 'enum_field', GenericEnum.FIRST.name).count() == 1
        assert filter_enum(EnumObject.objects.all(), 'enum_field', GenericEnum.SECOND.name).count() == 0

        with pytest.raises(ValidationError):
            filter_enum(EnumObject.objects.all(), 'enum_field', 'FOURTH')

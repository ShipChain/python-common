import pytest
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from src.shipchain_common.filters import filter_enum
from tests.models import EnumObject


class EnumObjectModel(TestCase):
    def test_enum_filter(self):
        EnumObject.objects.create(enum_field=0)
        assert filter_enum(EnumObject.objects.all(), 'enum_field', 'FIRST').count() == 1
        assert filter_enum(EnumObject.objects.all(), 'enum_field', 'SECOND').count() == 0

        with pytest.raises(ValidationError):
            filter_enum(EnumObject.objects.all(), 'enum_field', 'FOURTH')

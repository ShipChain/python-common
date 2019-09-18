import pytest
import uuid
from unittest.mock import patch

from django.utils import timezone

from src.shipchain_common.utils import random_id, tznow

TEST_UUIDS = ['uuid_{}'.format(i) for i in range(10000)]

MOCK_NOW = timezone.now()


@pytest.fixture
def test_uuids():
    return ['uuid_{}'.format(i) for i in range(10000)]


@pytest.fixture
def mock_now():
    return timezone.now()


def test_random_id(test_uuids):
    def uuid_prefix(prefix: str):
        return patch.object(uuid, 'uuid4', side_effect=['{}_{}'.format(prefix, x) for x in test_uuids])

    with uuid_prefix('test1'):
        test1 = random_id()
        assert type(test1) == str
        assert test1 == 'test1_uuid_0'


def test_tznow(mock_now):

    def get_mock_now():
        return mock_now

    def mock_time():
        return patch.object(timezone, 'now', side_effect=get_mock_now)

    with mock_time():
        now = tznow()
        assert now == mock_now

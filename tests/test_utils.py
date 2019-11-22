import pytest
import uuid
from unittest.mock import patch
from unittest.case import TestCase
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from src.shipchain_common.utils import assertDeepAlmostEqual, random_id, tznow, snake_to_sentence, validate_uuid4
from src.shipchain_common.test_utils import datetimeAlmostEqual

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


def test_uuid4_validator():
    valid_uuid4 = str(uuid.uuid4())
    assert validate_uuid4(valid_uuid4)
    uuid4_no_dashes = valid_uuid4.replace('-', '')
    assert not validate_uuid4(uuid4_no_dashes)
    hex32str = '08E7CF0B-97F3-04A0-4377-B989DC61B100'
    assert not validate_uuid4(hex32str)
    garbage = 'ga-r-b-age'
    assert not validate_uuid4(garbage)


def test_tznow(mock_now):

    def get_mock_now():
        return mock_now

    def mock_time():
        return patch.object(timezone, 'now', side_effect=get_mock_now)

    with mock_time():
        now = tznow()
        assert now == mock_now


def test_snake_to_sentence():
    snake_case = "Lorem_ipsum_dolor_sit_amet,_consectetur_adipiscing_elit,"
    unsnaked = snake_to_sentence(snake_case)
    assert unsnaked == 'Lorem Ipsum Dolor Sit Amet, Consectetur Adipiscing Elit,'


def test_datetimeAlmostEqual(mock_now):
    date_time_1 = mock_now + timedelta(milliseconds=settings.MILLISECONDS_THRESHOLD - 1)
    date_time_2 = mock_now + timedelta(milliseconds=settings.MILLISECONDS_THRESHOLD + 1)
    date_time_3 = mock_now - timedelta(milliseconds=settings.MILLISECONDS_THRESHOLD - 1)
    date_time_4 = mock_now - timedelta(milliseconds=settings.MILLISECONDS_THRESHOLD + 1)

    assert datetimeAlmostEqual(mock_now, dt2=date_time_1)
    assert not datetimeAlmostEqual(mock_now, dt2=date_time_2)

    assert datetimeAlmostEqual(mock_now, dt2=date_time_3)
    assert not datetimeAlmostEqual(mock_now, dt2=date_time_4)


class UtilsTests(TestCase):
    def test_assert_almost_equal(self):
        assertDeepAlmostEqual(self,
                              expected={
                                  'data': {
                                      'testing': 123.4567890123456789
                                  }
                              },
                              actual={
                                  'data': {
                                      'testing': 123.4567890123456788
                                  }
                              })
        self.assertRaises(AssertionError, assertDeepAlmostEqual,
                          test_case=self,
                          expected={
                              'testing': 123
                          },
                          actual={
                              'testing': 124
                          })

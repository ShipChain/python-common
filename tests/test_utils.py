import pytest
import uuid
from unittest.mock import patch
from unittest.case import TestCase

from django.utils import timezone

from src.shipchain_common.utils import assertDeepAlmostEqual, random_id, tznow, snake_to_sentence
from src.shipchain_common.test_utils import datetimeAlmostEqual, MICROSECONDS_THRESHOLD

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


def test_snake_to_sentence():
    snake_case = "Lorem_ipsum_dolor_sit_amet,_consectetur_adipiscing_elit,"
    unsnaked = snake_to_sentence(snake_case)
    assert unsnaked == 'Lorem Ipsum Dolor Sit Amet, Consectetur Adipiscing Elit,'


def test_datetimeAlmostEqual(mock_now):
    date_time_1 = mock_now.replace(second=0, microsecond=0)
    date_time_2 = mock_now.replace(second=0, microsecond=MICROSECONDS_THRESHOLD - 1)
    date_time_3 = mock_now.replace(second=0, microsecond=MICROSECONDS_THRESHOLD + 1)

    assert datetimeAlmostEqual(date_time_1, dt2=date_time_2)
    assert not datetimeAlmostEqual(date_time_1, dt2=date_time_3)


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

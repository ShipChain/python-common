import json

import pytest
from rest_framework import status
import requests
from datetime import datetime
from copy import deepcopy

from src.shipchain_common.test_utils import HTTPrettyAsserter

CURRENT_TIME = datetime.now()


@pytest.yield_fixture
def modified_http_pretty():
    HTTPrettyAsserter.enable(allow_net_connect=False)
    yield HTTPrettyAsserter
    HTTPrettyAsserter.disable()


@pytest.fixture
def query_string(query_dict):
    return f'?query_param_1={1}&query_param_2={2}&query_param_bool={False}&datetime={CURRENT_TIME}'


@pytest.fixture
def modified_query_string(query_string):
    return f'{query_string}&query_param_3=3'


@pytest.fixture
def query_dict():
    return {
        'query_param_1': 1,
        'query_param_2': 2,
        'query_param_bool': False,
        'datetime': str(CURRENT_TIME)
    }


@pytest.fixture
def modified_query_dict():
    return {
        'query_param_1': 1,
        'query_param_2': 2,
        'query_param_bool': False,
        'datetime': str(CURRENT_TIME),
        'query_param_3': 3,
    }


@pytest.fixture
def http_pretty_list_mocking(modified_http_pretty):
    modified_http_pretty.register_uri(modified_http_pretty.POST, 'http://google.com/path', status=status.HTTP_200_OK)
    modified_http_pretty.register_uri(modified_http_pretty.POST, 'http://google.com/path', status=status.HTTP_200_OK)
    modified_http_pretty.register_uri(modified_http_pretty.POST, 'http://google.com/other_path',
                                      status=status.HTTP_200_OK)
    modified_http_pretty.register_uri(modified_http_pretty.POST, 'http://bing.com/bing_path',
                                      status=status.HTTP_200_OK)
    return modified_http_pretty


@pytest.fixture
def successful_body():
    return {
        'integer': 1,
        'datetime': str(CURRENT_TIME),
        'string': 'string',
        'dictionary': {
            'string': 'new_string'
        },
        'array': [0, 1, 2]
    }


@pytest.fixture
def successful_urlencoded_body():
    return {
        'integer': 1,
        'datetime': str(CURRENT_TIME),
        'string': 'string',
        'array': [0, 1, 2]
    }


@pytest.fixture
def successful_json_body():
    return json.dumps({
        'integer': 1,
        'datetime': str(CURRENT_TIME),
        'dictionary': {
            'string': 'new_string'
        },
        'array': [0, 1, 2],
        'string': 'string'
    })


@pytest.fixture
def successful_assertions(query_dict, successful_body, successful_urlencoded_body):
    modified_query_dict = deepcopy(query_dict)
    modified_query_dict['query_param_3'] = 3
    return [{
        'path': '/path',
        'body': successful_body,
        'query': query_dict,
        'host': 'google.com',
    }, {
        'path': '/path',
        'body': {},
        'query': modified_query_dict,
        'host': 'google.com',
    }, {
        'path': '/bing_path',
        'body': successful_urlencoded_body,
        'host': 'bing.com',
    }]


@pytest.fixture
def single_assertions(query_dict, successful_body):
    return [{
        'path': '/path',
        'body': successful_body,
        'query': query_dict,
        'host': 'google.com',
    }]


@pytest.fixture
def failing_query_assertions(query_dict, successful_body):
    return [{
        'path': '/path',
        'query': query_dict,
        'host': 'google.com',
    }]


@pytest.fixture
def failing_host_assertions(query_dict, successful_body):
    return [{
        'path': '/path',
        'host': 'FAILING HOST',
    }]


@pytest.fixture
def no_host_assertions(query_dict, successful_body):
    return [{
        'path': '/path',
    }]


@pytest.fixture
def no_path_assertions(query_dict, successful_body):
    return [{
    }]


@pytest.fixture
def failing_path_assertions(query_dict, successful_body):
    return [{
        'path': 'FAILING PATH',
        'host': 'google.com',
    }]


@pytest.fixture
def dict_assertions(query_dict, successful_body):
    return {
        'path': '/path',
    }


class TestHttprettyList:
    def test_unsuccessful_empty_check(self, http_pretty_list_mocking, query_string, successful_json_body,
                                      single_assertions):
        requests.post('http://google.com/path' + query_string, data=successful_json_body,
                      headers={'content-type': 'application/json'})
        requests.post('http://google.com/path')

        # Ensure that after all calls were checked, assert all calls checked is accurate
        with pytest.raises(AssertionError) as err:
            http_pretty_list_mocking.assert_calls(single_assertions)
        assert f"Difference in expected call count, 2 made asserted 1. Calls: " in str(err.value)

    def test_successful_mocking(self, http_pretty_list_mocking, query_string, successful_assertions, successful_body,
                                successful_json_body, modified_query_string, successful_urlencoded_body):
        requests.post('http://google.com/path' + query_string, data=successful_json_body,
                      headers={'content-type': 'application/json'})
        requests.post('http://google.com/path' + modified_query_string, data='')
        requests.post('http://bing.com/bing_path', data=successful_urlencoded_body,
                      headers={'content-type': 'application/x-www-form-urlencoded'})
        http_pretty_list_mocking.assert_calls(successful_assertions)

    def test_unsuccessful_query_check(self, http_pretty_list_mocking, modified_query_string, failing_query_assertions,
                                      query_dict, modified_query_dict, successful_body):
        requests.post('http://google.com/path' + modified_query_string, data='')
        with pytest.raises(AssertionError) as err:
            http_pretty_list_mocking.assert_calls(failing_query_assertions)
        assert f'Error: query mismatch, desired `{query_dict}` returned `{modified_query_dict}`.' in str(err.value)

    def test_unsuccessful_path_check(self, http_pretty_list_mocking, failing_path_assertions):
        requests.post('http://google.com/other_path')
        with pytest.raises(AssertionError) as err:
            http_pretty_list_mocking.assert_calls(failing_path_assertions)
        assert f'Error: path mismatch, desired `FAILING PATH` returned `/other_path`.' in str(err.value)

    def test_no_path_check(self, http_pretty_list_mocking, no_path_assertions):
        requests.post('http://google.com/other_path')
        with pytest.raises(AssertionError) as err:
            http_pretty_list_mocking.assert_calls(no_path_assertions)
        assert 'Error: Must include path in assertion.' in str(err.value)

    def test_unsuccessful_host_check(self, http_pretty_list_mocking, failing_host_assertions):
        requests.post('http://google.com/path')
        with pytest.raises(AssertionError) as err:
            http_pretty_list_mocking.assert_calls(failing_host_assertions)
        assert f'Error: host mismatch, desired `FAILING HOST` returned `google.com`.' in str(err.value)

    def test_no_host_check(self, http_pretty_list_mocking, no_host_assertions):
        requests.post('http://google.com/path')
        with pytest.raises(AssertionError) as err:
            http_pretty_list_mocking.assert_calls(no_host_assertions)
        assert 'Error: Must include host in assertion.' in str(err.value)

    def test_non_list_assertion(self, http_pretty_list_mocking, dict_assertions):
        requests.post('http://google.com/path')
        with pytest.raises(AssertionError) as err:
            http_pretty_list_mocking.assert_calls(dict_assertions)
        assert f'Error: asserted calls should be of type `list` not of type `{type(dict_assertions)}`' in str(err.value)

    def test_no_calls_made(self, http_pretty_list_mocking, successful_assertions):
        with pytest.raises(AssertionError) as err:
            http_pretty_list_mocking.assert_calls(successful_assertions)
        assert f'Error: No calls made to be parsed.' in str(err.value)

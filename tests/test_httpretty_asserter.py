import pytest
import httpretty
from rest_framework import status
import requests
from datetime import datetime
from copy import deepcopy

from src.shipchain_common.test_utils import HttprettyAsserterMixin


CURRENT_TIME = datetime.now()


@pytest.yield_fixture
def http_pretty():
    httpretty.enable(allow_net_connect=False)
    yield httpretty
    httpretty.disable()


@pytest.fixture
def query_params():
    query_params = {
        'string': f'?query_param_1={1}&query_param_2={2}&query_param_bool={False}&datetime={CURRENT_TIME}',
        'dict': {
            'query_param_1': 1,
            'query_param_2': 2,
            'query_param_bool': False,
            'datetime': CURRENT_TIME
        }
    }
    return query_params


@pytest.fixture
def http_pretty_list_mocking(http_pretty):
    http_pretty.register_uri(http_pretty.POST, 'http://google.com/path', status=status.HTTP_200_OK)
    http_pretty.register_uri(http_pretty.POST, 'http://google.com/path', status=status.HTTP_200_OK)
    http_pretty.register_uri(http_pretty.POST, 'http://google.com/other_path', status=status.HTTP_200_OK)
    http_pretty.register_uri(http_pretty.POST, 'http://bing.com/bing_path', status=status.HTTP_200_OK)
    return http_pretty


class TestHttprettyList(HttprettyAsserterMixin):
    def test_successful_mocking(self, http_pretty_list_mocking, query_params):
        requests.post('http://google.com/path' + query_params['string'], data='')
        requests.post('http://google.com/path' + query_params['string'] + '&query_param_3=3', data='')
        requests.post('http://google.com/other_path' + query_params['string'], data={'body': 1})
        requests.post('http://bing.com/bing_path' + query_params['string'], data='')
        self.parse_calls_into_list(http_pretty_list_mocking)
        self.assert_call_in_list(3, path='/bing_path', query=query_params['dict'])
        self.assert_call_in_list(2, path='/other_path', query=query_params['dict'], body={'body': 1})
        self.assert_call_in_list(0, path='/path', query=query_params['dict'], body={})
        query_params['dict']['query_param_3'] = 3

        self.assert_call_in_list(1, path='/path', query=query_params['dict'], body={})

        # Ensure that after all calls were checked, assert all calls checked is accurate
        self.assert_all_list_calls_checked()

    def test_unsuccessful_empty_check(self, http_pretty_list_mocking, query_params):
        requests.post('http://google.com/path' + query_params['string'], data='')
        requests.post('http://google.com/path')
        self.parse_calls_into_list(http_pretty_list_mocking)
        self.assert_call_in_list(0, path='/path', query=query_params['dict'], body={})
        query_params['dict']['query_param_3'] = 3

        empty_call = {
            'path': '/path',
            'querystring': {},
            'body': {}
        }

        # Ensure that after all calls were checked, assert all calls checked is accurate
        with pytest.raises(AssertionError) as err:
            self.assert_all_list_calls_checked()
        assert f"Error these calls have not been checked: [{empty_call}]." in str(err.value)

    def test_unsuccessful_query_check(self, http_pretty_list_mocking, query_params):
        requests.post('http://google.com/path' + query_params['string'] + '&query_param_3=3', data='')
        self.parse_calls_into_list(http_pretty_list_mocking)
        different_query_params = deepcopy(query_params['dict'])
        different_query_params['query_param_3'] = 3
        with pytest.raises(AssertionError) as err:
            self.assert_call_in_list(0, '/path', query=query_params['dict'])
        assert f'Error: query mismatch, desired {query_params["dict"]} returned {different_query_params}.' \
               in str(err.value)

    def test_unsuccessful_path_check(self, http_pretty_list_mocking, query_params):
        requests.post('http://google.com/other_path')
        self.parse_calls_into_list(http_pretty_list_mocking)
        with pytest.raises(AssertionError) as err:
            self.assert_call_in_list(0, '/path')
        assert f'Error: path mismatch, desired /path returned /other_path.' in str(err.value)

    def test_unsuccessful_body_check(self, http_pretty_list_mocking, query_params):
        returned_body = {'int': 1, 'datetime': CURRENT_TIME}
        desired_body = {'datetime': CURRENT_TIME}
        requests.post('http://google.com/path', data=returned_body)
        self.parse_calls_into_list(http_pretty_list_mocking)
        with pytest.raises(AssertionError) as err:
            self.assert_call_in_list(0, '/path', body=desired_body)
        assert f'Error: body mismatch, desired {desired_body} returned {returned_body}.' in str(err.value)

    def test_no_calls_made(self, http_pretty_list_mocking):
        with pytest.raises(AssertionError) as err:
            self.parse_calls_into_list(http_pretty_list_mocking)
        assert f'Error: No calls made to be parsed.' in str(err.value)


class TestHttprettyDict(HttprettyAsserterMixin):
    def test_successful_list_mocking(self, http_pretty_list_mocking, query_params):
        requests.post('http://google.com/path' + query_params['string'] + '&query_param_3=3', data='')
        requests.post('http://google.com/other_path' + query_params['string'], data={'body': 1})
        requests.post('http://bing.com/bing_path' + query_params['string'], data='')
        self.parse_calls_into_dict(http_pretty_list_mocking)
        self.assert_call_in_dict(path='/other_path', query=query_params['dict'], body={'body': 1})
        self.assert_call_in_dict(path='/bing_path', query=query_params['dict'], body={})
        query_params['dict']['query_param_3'] = 3

        self.assert_call_in_dict(path='/path', query=query_params['dict'], body={})

        # Ensure that after all calls were checked, assert all calls checked is accurate
        self.assert_all_dict_calls_checked()

    def test_unsuccessful_empty_check(self, http_pretty_list_mocking, query_params):
        requests.post('http://google.com/path' + query_params['string'], data='')
        requests.post('http://google.com/other_path')
        self.parse_calls_into_dict(http_pretty_list_mocking)
        self.assert_call_in_dict(path='/path', query=query_params['dict'], body={})

        empty_call_dict = {
            '/other_path': {
                'querystring': {},
                'body': {}
            }
        }

        # Ensure that after all calls were checked, assert all calls checked is accurate
        with pytest.raises(AssertionError) as err:
            self.assert_all_dict_calls_checked()
        assert f"Error these calls have not been checked: {empty_call_dict}." in str(err.value)

    def test_no_calls_made_dict(self, http_pretty_list_mocking):
        with pytest.raises(AssertionError) as err:
            self.parse_calls_into_dict(http_pretty_list_mocking)
        assert f'Error: No calls made to be parsed.' in str(err.value)

    def test_unsuccessful_body_check_dict(self, http_pretty_list_mocking, query_params):
        returned_body = {'int': 1, 'datetime': CURRENT_TIME}
        desired_body = {'datetime': CURRENT_TIME}
        requests.post('http://google.com/path', data=returned_body)
        self.parse_calls_into_dict(http_pretty_list_mocking)
        with pytest.raises(AssertionError) as err:
            self.assert_call_in_dict('/path', body=desired_body)
        assert f'Error: body mismatch, desired {desired_body} returned {returned_body}.' in str(err.value)

    def test_unsuccessful_path_check(self, http_pretty_list_mocking, query_params):
        requests.post('http://google.com/other_path')
        self.parse_calls_into_dict(http_pretty_list_mocking)
        empty_call_dict = {
            '/other_path': {
                'querystring': {},
                'body': {}
            }
        }

        with pytest.raises(AssertionError) as err:
            self.assert_call_in_dict('/path')
        assert f'Error: /path not found in calls_dict: {empty_call_dict}.' in str(err.value)

    def test_unsuccessful_query_check_dict(self, http_pretty_list_mocking, query_params):
        requests.post('http://google.com/path' + query_params['string'] + '&query_param_3=3', data='')
        self.parse_calls_into_dict(http_pretty_list_mocking)
        different_query_params = deepcopy(query_params['dict'])
        different_query_params['query_param_3'] = 3
        with pytest.raises(AssertionError) as err:
            self.assert_call_in_dict('/path', query=query_params['dict'])
        assert f'Error: query mismatch, desired {query_params["dict"]} returned {different_query_params}.' \
               in str(err.value)

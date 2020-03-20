"""
Copyright 2020 ShipChain, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import pytest
from httpretty import HTTPretty

from urllib.parse import urlparse
from ..utils import parse_urlencoded_data


class HTTPrettyAsserter(HTTPretty):
    @classmethod
    def _parse_calls_into_list(cls):
        calls_list = []
        assert cls.latest_requests, 'Error: No calls made to be parsed.'
        for index, call in enumerate(cls.latest_requests):
            if call is None:
                # If calling cls.reset(), latest_requests are unable to build.
                # Setting the current call to None and iterating through this way ensures that only calls from the
                # individual test are set in the call_list.
                continue

            url = urlparse(call.path)
            if call.headers.get('content-type', '') in ('application/json', 'text/json'):
                body = call.parsed_body
            else:
                body = parse_urlencoded_data(call.body.decode())

            calls_list.append({
                'path': url.path,
                'query': parse_urlencoded_data(url.query),
                'body': body,
                'host': call.headers.get('host', '')
            })
            cls.latest_requests[index] = None
        assert calls_list, 'Error: No calls made to be parsed.'
        return calls_list

    @classmethod
    def assert_calls(cls, asserted_calls):
        calls_list = cls._parse_calls_into_list()
        assert isinstance(asserted_calls, list),\
            f'Error: asserted calls should be of type `list` not of type `{type(asserted_calls)}`'
        assert len(calls_list) == len(asserted_calls), f'Difference in expected call count, {len(calls_list)}' \
                                                       f' made asserted {len(asserted_calls)}. Calls: {calls_list}'
        for index, _ in enumerate(calls_list):
            cls._assert_call_in_list(calls_list[index], asserted_calls[index])

    @classmethod
    def _assert_call_in_list(cls, call, assertion):
        assert 'path' in assertion, 'Error: Must include path in assertion.'
        assert assertion["path"] == call['path'],\
            f'Error: path mismatch, desired `{assertion["path"]}` returned `{call["path"]}`.'
        assert 'host' in assertion, 'Error: Must include host in assertion.'
        assert call['host'] in assertion["host"],\
            f'Error: host mismatch, desired `{assertion["host"]}` returned `{call["host"]}`.'
        if 'body' in assertion:
            assert assertion['body'] == call['body'], \
                f'Error: body mismatch, desired `{assertion["body"]}` returned `{call["body"]}`.'
        if 'query' in assertion:
            assert assertion['query'] == call['query'], \
                f'Error: query mismatch, desired `{assertion["query"]}` returned `{call["query"]}`.'


@pytest.yield_fixture
def modified_http_pretty():
    HTTPrettyAsserter.enable(allow_net_connect=False)
    yield HTTPrettyAsserter
    HTTPrettyAsserter.disable()

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
import responses

from urllib.parse import urlparse
from ..utils import parse_urlencoded_data, parse_value


class ResponsesHTTPrettyWrapper:
    def __init__(self):
        self.mock = responses.mock

    def __getattr__(self, item):
        return getattr(self.mock, item)

    def register_uri(self,  # noqa
                     method,
                     uri,
                     body="HTTPretty :)",
                     adding_headers=None,
                     status=200,
                     match_querystring=False,
                     **headers
                     ):
        try:
            self.mock.replace(method_or_response=method, url=uri, body=body, status=status,
                              match_querystring=match_querystring, headers=headers)
        except ValueError:
            self.mock.add(method=method, url=uri, body=body, status=status,
                          adding_headers=adding_headers, match_querystring=match_querystring, headers=headers)

    class Call:
        def __init__(self, responses_call):
            self.call = responses_call
            self.url = urlparse(self.call.request.url)

        def __getattr__(self, item):
            return getattr(self.call, item)

        @property
        def parsed_body(self):
            body = self.call.request.body or ''
            if self.call.request.headers.get('content-type', '') in ('application/json', 'text/json'):
                body = parse_value(body)
            else:
                body = parse_urlencoded_data(body)

            return body

        @property
        def querystring(self):
            return parse_urlencoded_data(self.url.query)


    @property
    def latest_requests(self):
        return [self.Call(call) for call in self.mock.calls]

    def last_request(self):
        return self.Call(self.mock.calls[-1]) if self.mock.calls else None

    def reset(self):
        self.mock._calls.reset()  # pylint:disable=protected-access


class ResponsesAsserter(ResponsesHTTPrettyWrapper):
    def _parse_calls_into_list(self):
        calls_list = []
        assert self.latest_requests, 'Error: No calls made to be parsed.'
        for call in self.latest_requests:
            calls_list.append({
                'path': call.url.path,
                'query': call.querystring,
                'body': call.parsed_body,
                'host': call.url.hostname
            })
        assert calls_list, 'Error: No calls made to be parsed.'
        return calls_list

    def assert_calls(self, asserted_calls):
        calls_list = self._parse_calls_into_list()
        assert isinstance(asserted_calls, list), \
            f'Error: asserted calls should be of type `list` not of type `{type(asserted_calls)}`'
        assert len(calls_list) == len(asserted_calls), f'Difference in expected call count, {len(calls_list)}' \
                                                       f' made asserted {len(asserted_calls)}. Calls: {calls_list}'
        for index, _ in enumerate(calls_list):
            self._assert_call_in_list(calls_list[index], asserted_calls[index])

        self.reset_calls()

    def _assert_call_in_list(self, call, assertion):
        assert 'path' in assertion, 'Error: Must include path in assertion.'
        assert assertion["path"] == call['path'], \
            f'Error: path mismatch, desired `{assertion["path"]}` returned `{call["path"]}`.'
        assert 'host' in assertion, 'Error: Must include host in assertion.'
        assert call['host'] in assertion["host"], \
            f'Error: host mismatch, desired `{assertion["host"]}` returned `{call["host"]}`.'
        if 'body' in assertion:
            assert assertion['body'] == call['body'], \
                f'Error: body mismatch, desired `{assertion["body"]}` returned `{call["body"]}`.'
        if 'query' in assertion:
            assert assertion['query'] == call['query'], \
                f'Error: query mismatch, desired `{assertion["query"]}` returned `{call["query"]}`.'

    def reset_calls(self):
        self.reset()


@pytest.yield_fixture(scope='function')
def modified_responses():
    responses.start()
    responses_asserter = ResponsesAsserter()
    yield responses_asserter
    responses_asserter.reset_calls()
    try:
        responses.stop()
    except RuntimeError:
        # Ignore unittest.mock "stop called on unstarted patcher" exception
        pass


# Deprecated names for backwards-compatibility
HTTPrettyAsserter = ResponsesAsserter
modified_http_pretty = modified_responses

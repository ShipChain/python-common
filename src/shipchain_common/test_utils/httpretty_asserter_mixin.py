import json

import dateutil


class HttprettyAsserterMixin:
    def _parse_item(self, item):
        if item in ['False', 'false']:
            return False
        if item in ['True', 'true']:
            return True
        try:
            parsed = json.loads(item)
        except ValueError:
            parsed = item
        try:
            return dateutil.parser.parse(parsed)
        except (ValueError, TypeError):
            pass
        return parsed

    def _parse_list(self, to_parse_list):
        parsed_list = []
        for item in to_parse_list:
            if isinstance(item, list):
                parsed_list.append(self._parse_list(item))
            else:
                parsed_list.append(self._parse_item(item))
        return parsed_list

    def _parse_dict(self, body):
        parsed_body = {}
        for key in body:
            if isinstance(body[key], list) and len(body[key]) > 1:
                parsed_body[key] = self._parse_list(body[key])
            else:
                parsed_body[key] = self._parse_item(body[key][0])
        return parsed_body

    def _assert_query_and_body(self, call, body=None, query=None):
        if not (body is None):
            assert call['body'] == body, f'Error: body mismatch, desired {body} returned {call["body"]}.'
        if not (query is None):
            assert call['querystring'] == query,\
                f'Error: query mismatch, desired {query} returned {call["querystring"]}.'

    def parse_calls_into_list(self, httpretty_mocking):
        self.calls_list = []
        assert httpretty_mocking.latest_requests(), 'Error: No calls made to be parsed.'
        for call in httpretty_mocking.latest_requests():
            parsed_path = call.path.split("?")[0]
            self.calls_list.append({
                'path': parsed_path,
                'querystring': self._parse_dict(call.querystring),
                'body': self._parse_dict(call.parsed_body)
            })
        httpretty_mocking.reset()

    def parse_calls_into_dict(self, httpretty_mocking):
        self.calls_dict = {}
        assert httpretty_mocking.latest_requests(), 'Error: No calls made to be parsed.'
        for call in httpretty_mocking.latest_requests():
            parsed_path = call.path.split("?")[0]

            self.calls_dict[parsed_path] = {
                    'querystring': self._parse_dict(call.querystring),
                    'body': self._parse_dict(call.parsed_body)
                }
        httpretty_mocking.reset()

    def assert_call_in_list(self, index, path, body=None, query=None):
        assert self.calls_list, 'Error, calls have not been parsed yet.'
        assert index <= (len(self.calls_list) - 1), f'Error: index {index} exists outside of calls_list scope.'
        call = self.calls_list[index]
        assert path == call['path'], f'Error: path mismatch, desired {path} returned {call["path"]}.'
        self._assert_query_and_body(call, body=body, query=query)
        # This is so that you can ensure that no calls were made by checking assert_all_list_calls_checked
        self.calls_list[index] = None

    def assert_call_in_dict(self, path, body=None, query=None):
        assert self.calls_dict, 'Error, calls have not been parsed yet.'
        assert path in self.calls_dict, f'Error: {path} not found in calls_dict: {self.calls_dict}.'
        assert self.calls_dict[path], f'Error: {path} in calls_dict is empty. Has it already been tested?'
        call = self.calls_dict[path]
        self._assert_query_and_body(call, body=body, query=query)
        # This is so that you can ensure that no calls were made by checking assert_all_dict_calls_checked
        del self.calls_dict[path]

    def assert_all_list_calls_checked(self):
        non_checked_calls = []
        for call in self.calls_list:
            if not (call is None):
                non_checked_calls.append(call)

        assert non_checked_calls == [], f'Error these calls have not been checked: {non_checked_calls}.'

    def assert_all_dict_calls_checked(self):
        assert self.calls_dict == {}, f'Error these calls have not been checked: {self.calls_dict}.'

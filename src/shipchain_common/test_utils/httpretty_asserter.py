import json

from httpretty import HTTPretty


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
            parsed_path = call.path.split("?")[0]
            if call.headers.get('content-type', '') not in ('application/json', 'text/json'):
                parsed_body = cls._parse_dict(call.parsed_body)
            else:
                parsed_body = call.parsed_body
            calls_list.append({
                'path': parsed_path,
                'query': cls._parse_dict(call.querystring),
                'body': parsed_body,
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
    def _parse_item(cls, item):
        if item in ['False', 'false']:
            return False
        if item in ['True', 'true']:
            return True
        try:
            parsed = json.loads(item)
        except ValueError:
            parsed = item
        return parsed

    @classmethod
    def _parse_list(cls, to_parse_list):
        parsed_list = []
        for item in to_parse_list:
            if isinstance(item, list):
                parsed_list.append(cls._parse_list(item))
            else:
                parsed_list.append(cls._parse_item(item))
        return parsed_list

    @classmethod
    def _parse_dict(cls, body):
        parsed_body = {}
        for key in body:
            if isinstance(body[key], list):
                if len(body[key]) > 1:
                    parsed_body[key] = cls._parse_list(body[key])

                else:
                    parsed_body[key] = cls._parse_item(body[key][0])
        return parsed_body

    @classmethod
    def _assert_call_in_list(cls, call, assertion):
        assert 'path' in assertion, 'Error: Must include path in assertion.'
        assert assertion["path"] == call['path'],\
            f'Error: path mismatch, desired `{assertion["path"]}` returned `{call["path"]}`.'
        assert 'host' in assertion, 'Error: Must include host in assertion.'
        assert call['host'] in assertion["host"],\
            f'Error: host mismatch, desired `{assertion["host"]}` returned `{call["host"]}`.'
        if 'body' in assertion:
            assert call['body'] == assertion['body'],\
                f'Error: body mismatch, desired `{assertion["body"]}` returned `{call["body"]}`.'
        if 'query' in assertion:
            assert call['query'] == assertion["query"], \
                f'Error: query mismatch, desired `{assertion["query"]}` returned `{call["query"]}`.'

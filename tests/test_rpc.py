import pytest
from unittest import mock

import requests
from django.conf import settings

from src.shipchain_common.exceptions import RPCError
from src.shipchain_common.rpc import RPCClient
from src.shipchain_common.test_utils import mocked_rpc_response


@pytest.fixture(scope='module')
def rpc_settings():
    settings.ENGINE_RPC_URL = 'http://INTENTIONALLY_DISCONNECTED:9999'


@pytest.fixture()
def rpc_client(rpc_settings):
    return RPCClient()


def test_rpc_init(rpc_client):
    assert rpc_client.url == settings.ENGINE_RPC_URL

    assert 'jsonrpc' in rpc_client.payload
    assert 'id' in rpc_client.payload
    assert 'params' in rpc_client.payload
    assert rpc_client.url == 'http://INTENTIONALLY_DISCONNECTED:9999'
    assert rpc_client.payload['id'] == 0
    assert rpc_client.payload['params'] == {}


def test_call(rpc_client):

    # Call without the backend should return the 503 RPCError
    with mock.patch.object(requests.Session, 'post') as mock_method:
        mock_method.side_effect = requests.exceptions.ConnectionError(mock.Mock(status=503), 'not found')

        with pytest.raises(RPCError) as rpc_error:
            rpc_client.call('test_method')
        assert rpc_error.value.status_code == 503
        assert rpc_error.value.detail == 'Service temporarily unavailable, try again later'

    # Error response from RPC Server should return server detail in exception
    with mock.patch.object(requests.Session, 'post') as mock_method:
        mock_method.return_value = mocked_rpc_response({
            "error": {
                "code": 1337,
                "message": "Error from RPC Server",
            },
        })

        with pytest.raises(RPCError) as rpc_error:
            rpc_client.call('test_method')

        assert rpc_error.value.status_code == 500
        assert rpc_error.value.detail == 'Error from RPC Server'

        # Response object from server should be returned on success
        mock_method.return_value = mocked_rpc_response({
            "jsonrpc": "2.0",
            "result": {
                "success": True,
                "test_object": {
                    "id": "d5563423-f040-4e0d-8d87-5e941c748d91",
                }
            },
            "id": 0
        })

        response_json = rpc_client.call('test_method')
        assert response_json['test_object'] == {"id": "d5563423-f040-4e0d-8d87-5e941c748d91"}

    with mock.patch.object(requests.Session, 'post') as mock_request_post:
        unexpected_error = b'Unexpected server error'
        mock_request_post.return_value = mocked_rpc_response(unexpected_error, content=unexpected_error,
                                                             code=406)

        with pytest.raises(RPCError) as rpc_error:

            rpc_client.call('test_method')

        assert rpc_error.value.status_code == 500
        assert str(rpc_error.value) == str(unexpected_error)


import pytest
from unittest import mock

import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
from django.conf import settings

from src.shipchain_common.exceptions import AWSIoTError
from src.shipchain_common.iot import AWSIoTClient
from src.shipchain_common.test_utils import mocked_rpc_response


@pytest.fixture(scope='module')
def iot_settings():
    settings.IOT_THING_INTEGRATION = True
    settings.IOT_AWS_HOST = 'not-really-aws.com'
    settings.IOT_GATEWAY_STAGE = 'test'


@pytest.fixture()
def aws_iot_client(iot_settings):
    return AWSIoTClient()


class FakeBotoAWSRequestsAuth(BotoAWSRequestsAuth):
    def __init__(self, *args, **kwargs):
        pass

    def get_aws_request_headers_handler(self, r):
        return {}


def test_init(iot_settings, aws_iot_client):

    assert settings.IOT_GATEWAY_STAGE == 'test'
    assert aws_iot_client.session.auth.aws_host == 'not-really-aws.com'
    assert aws_iot_client.session.auth.aws_region == 'us-east-1'
    assert aws_iot_client.session.auth.service == 'execute-api'
    assert aws_iot_client.session.auth.aws_secret_access_key is None
    assert 'content-type' in aws_iot_client.session.headers
    assert aws_iot_client.session.headers['content-type'] == 'application/json'


def test_get(aws_iot_client):

    # Call without connection return the 503 Error
    with mock.patch.object(requests.Session, 'get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError(mock.Mock(status=503), 'not found')
        with pytest.raises(AWSIoTError) as aws_error:
            aws_iot_client._get('test_method')
            assert aws_error.status_code == 503

    with mock.patch.object(requests.Session, 'get') as mock_get:
        mock_get.return_value = mocked_rpc_response({
            "error": {
                "code": 1337,
                "message": "Error from AWS Server",
            },
        })

        try:
            aws_iot_client._get('test_method')
        except AWSIoTError as aws_error:
            assert aws_error.status_code == 500
            assert 'Error from AWS Server' in aws_error.detail

        mock_get.return_value = mocked_rpc_response({
            "error": {
                "code": 404,
                "message": "Error from AWS Server",
            },
        }, code=404)

        with pytest.raises(AWSIoTError) as aws_error:
            aws_iot_client._get('test_method')
            assert aws_error.status_code == 500
            assert 'Error from AWS Server' in aws_error.detail

        mock_get.side_effect = KeyError('Generic Exception')
        with pytest.raises(AWSIoTError) as aws_error:
            aws_iot_client._get('test_method')
            assert aws_error.status_code == 500


def test_call(aws_iot_client):

    # Call without connection return the 503 Error
    with mock.patch.object(requests.Session, 'post') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError(mock.Mock(status=503), 'not found')

        with pytest.raises(AWSIoTError) as aws_error:
            aws_iot_client._call('post', 'test_method')
            assert aws_error.status_code == 503

    with mock.patch.object(requests.Session, 'post') as mock_post:
        mock_post.return_value = mocked_rpc_response({
            "error": {
                "code": 404,
                "message": "Error from AWS Server",
            },
        }, code=404)

        with pytest.raises(AWSIoTError) as aws_error:
            aws_iot_client._call('post', 'test_method')
            assert aws_error.status_code == 500
            assert 'Error from AWS Server' in aws_error.detail

        mock_post.return_value = mocked_rpc_response({
            "message": {
                "code": 404,
                "message": "Error from AWS Server",
            },
        }, code=404)

        with pytest.raises(AWSIoTError) as aws_error:
            aws_iot_client._call('post', 'test_method')
            assert aws_error.status_code == 500
            assert 'Error from AWS Server' in aws_error.detail

        mock_post.return_value = mocked_rpc_response({
            "fail": {
                "code": 404,
                "message": "Error from AWS Server",
            },
        }, code=404)

        with pytest.raises(AWSIoTError) as aws_error:
            aws_iot_client._call('post', 'test_method')
            assert aws_error.status_code == 500
            assert 'Error from AWS Server' in aws_error.detail

        mock_post.return_value = mocked_rpc_response({
            "success": {
                "message": "Success from AWS Server",
            },
        }, code=404)

        with pytest.raises(AWSIoTError) as aws_error:
            aws_iot_client._call('patch', 'test_method')
            assert aws_error.status_code == 500
            assert 'Invalid HTTP Method' in aws_error.detail

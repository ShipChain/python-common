"""
Copyright 2019 ShipChain, Inc.

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

import json
import logging
import re

import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
from django.conf import settings
from rest_framework import status
from influxdb_metrics.loader import log_metric, TimingMetric

from .exceptions import AWSIoTError


LOG = logging.getLogger('python_common')


class AWSIoTClient:

    METHOD_POST = 'post'
    METHOD_PUT = 'put'
    METHOD_GET = 'get'
    METHOD_DELETE = 'delete'

    RESPONSE_200_METHODS = [METHOD_PUT, METHOD_GET, METHOD_DELETE]

    def __init__(self):
        aws_auth = BotoAWSRequestsAuth(
            aws_host=settings.IOT_AWS_HOST,
            aws_region='us-east-1',
            aws_service='execute-api'
        )

        self.session = requests.session()
        self.session.headers = {'content-type': 'application/json'}
        self.session.auth = aws_auth

    def _call(self, http_method, endpoint, payload=None, params=None):
        generic_endpoint = AWSIoTClient._get_generic_endpoint_for_metric(http_method, endpoint)

        if payload:
            payload = json.dumps(payload)

        url = f'https://{settings.IOT_AWS_HOST}/{settings.IOT_GATEWAY_STAGE}/{endpoint}'

        try:

            with TimingMetric('python_common_aws_iot.call', tags={'method': generic_endpoint}) as timer:

                if http_method == AWSIoTClient.METHOD_POST:
                    response = self.session.post(url, data=payload, params=params)
                    response_json = response.json()

                    if response.status_code != status.HTTP_201_CREATED:
                        self._process_error_object(generic_endpoint, response, response_json)

                elif http_method in AWSIoTClient.RESPONSE_200_METHODS:
                    response = getattr(self.session, http_method)(url, data=payload, params=params)
                    response_json = response.json()

                    if response.status_code != status.HTTP_200_OK:
                        self._process_error_object(generic_endpoint, response, response_json)

                else:
                    log_metric('python_common_aws_iot.error', tags={'method': generic_endpoint,
                                                                   'code': 'InvalidHTTPMethod'})
                    LOG.error('aws_iot_client(%s) error: %s', generic_endpoint, 'Invalid HTTP Method')
                    raise AWSIoTError(f'Invalid HTTP Method {http_method}')

                LOG.info('aws_iot_client(%s) duration: %.3f', generic_endpoint, timer.elapsed)

        except requests.exceptions.ConnectionError:
            log_metric('python_common_aws_iot.error', tags={'method': generic_endpoint, 'code': 'ConnectionError'})
            raise AWSIoTError("Service temporarily unavailable, try again later", status.HTTP_503_SERVICE_UNAVAILABLE,
                              'service_unavailable')

        except Exception as exception:
            log_metric('python_common_aws_iot.error', tags={'method': generic_endpoint, 'code': 'exception'})
            raise AWSIoTError(str(exception))

        return response_json

    def _post(self, endpoint, payload=None, query_params=None):
        return self._call(AWSIoTClient.METHOD_POST, endpoint, payload, params=query_params)

    def _put(self, endpoint, payload=None, query_params=None):
        return self._call(AWSIoTClient.METHOD_PUT, endpoint, payload, params=query_params)

    def _get(self, endpoint, query_params=None):
        return self._call(AWSIoTClient.METHOD_GET, endpoint, params=query_params)

    def _delete(self, endpoint, query_params=None):
        return self._call(AWSIoTClient.METHOD_DELETE, endpoint, params=query_params)

    @staticmethod
    def _get_generic_endpoint_for_metric(http_method, endpoint):
        generic_endpoint = re.sub(r'[0-9A-F]{8}-[0-9A-F]{4}-[4][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}',
                                  '<device_id>', endpoint, flags=re.IGNORECASE)

        return f'{http_method}::{generic_endpoint}'

    @staticmethod
    def _process_error_object(endpoint, response, response_json):
        error_code = response.status_code

        if 'error' in response_json:
            message = response_json['error']
            if isinstance(message, dict):
                if 'code' in message:
                    error_code = message['code']
                if 'message' in message:
                    message = message['message']

        elif 'message' in response_json:
            message = response_json['message']

        else:
            message = response_json

        log_metric('python_common_aws_iot.error', tags={'method': endpoint, 'code': error_code})
        LOG.error('aws_iot_client(%s) error: %s', endpoint, message)
        raise AWSIoTError(f'Error in AWS IoT Request: [{error_code}] {message}')

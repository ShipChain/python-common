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

import json
import logging

import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
from django.conf import settings
from influxdb_metrics.loader import log_metric, TimingMetric
from rest_framework import status

from .exceptions import AWSIoTError
from .utils import DecimalEncoder

LOG = logging.getLogger('python-common')


class AWSClient:
    @property
    def url(self):
        raise NotImplementedError

    @property
    def session(self):
        raise NotImplementedError

    METHOD_POST = 'post'
    METHOD_PUT = 'put'
    METHOD_GET = 'get'
    METHOD_DELETE = 'delete'

    RESPONSE_200_METHODS = [METHOD_PUT, METHOD_GET, METHOD_DELETE]

    def _call(self, http_method, endpoint, payload=None, params=None):
        metric_name = self._get_generic_endpoint_for_metric(http_method, endpoint)
        calling_url = f'{self.url}/{endpoint}'

        if payload:
            payload = json.dumps(payload, cls=DecimalEncoder)

        try:

            with TimingMetric('python_common_aws.call', tags={'method': metric_name}) as timer:

                if http_method == self.METHOD_POST:
                    response = self.session.post(calling_url, data=payload, params=params)
                    response_json = response.json()

                    if response.status_code != status.HTTP_201_CREATED:
                        self._process_error_object(metric_name, response, response_json)

                elif http_method in self.RESPONSE_200_METHODS:
                    response = getattr(self.session, http_method)(calling_url, data=payload, params=params)
                    response_json = response.json()

                    if response.status_code != status.HTTP_200_OK:
                        self._process_error_object(metric_name, response, response_json)

                else:
                    log_metric('python_common_aws.error', tags={'method': metric_name, 'code': 'InvalidHTTPMethod'})
                    LOG.error('aws_client(%s) error: %s', metric_name, 'Invalid HTTP Method')
                    raise AWSIoTError(f'Invalid HTTP Method {http_method}')

                LOG.info('aws_client(%s) duration: %.3f', metric_name, timer.elapsed)

        except requests.exceptions.ConnectionError:
            log_metric('python_common_aws.error', tags={'method': metric_name, 'code': 'ConnectionError'})
            raise AWSIoTError("Service temporarily unavailable, try again later", status.HTTP_503_SERVICE_UNAVAILABLE,
                              'service_unavailable')

        except Exception as exception:
            log_metric('python_common_aws.error', tags={'method': metric_name, 'code': 'exception'})
            raise AWSIoTError(str(exception))

        return response_json

    def _post(self, endpoint='', payload=None, query_params=None):
        return self._call(self.METHOD_POST, endpoint, payload, params=query_params)

    def _put(self, endpoint='', payload=None, query_params=None):
        return self._call(self.METHOD_PUT, endpoint, payload, params=query_params)

    def _get(self, endpoint='', query_params=None):
        return self._call(self.METHOD_GET, endpoint, params=query_params)

    def _delete(self, endpoint='', query_params=None):
        return self._call(self.METHOD_DELETE, endpoint, params=query_params)

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

        log_metric('python_common_aws.error', tags={'method': endpoint, 'code': error_code})
        LOG.error('aws_client(%s) error: %s', endpoint, message)
        raise AWSIoTError(f'Error in AWS IoT Request: [{error_code}] {message}')

    def _get_generic_endpoint_for_metric(self, http_method, endpoint):
        # This should be overwritten by each usage of this class for added clarity.
        return f'{http_method}::{endpoint}'


class URLShortenerClient(AWSClient):
    url = settings.URL_SHORTENER_URL
    session = requests.session()

    def __init__(self):
        aws_auth = BotoAWSRequestsAuth(
            aws_host=settings.URL_SHORTENER_HOST,
            aws_region='us-east-1',
            aws_service='execute-api'
        )

        self.session.headers = {'content-type': 'application/json'}
        self.session.auth = aws_auth

    def _get_generic_endpoint_for_metric(self, http_method, endpoint):
        return f'urlshortener::{http_method}::{endpoint}'

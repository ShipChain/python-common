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

import logging
import re

import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
from django.conf import settings

from .aws import AWSClient

LOG = logging.getLogger('python-common')


class AWSIoTClient(AWSClient):
    url = f'https://{settings.IOT_AWS_HOST}/{settings.IOT_GATEWAY_STAGE}'
    session = requests.session()

    def __init__(self):
        aws_auth = BotoAWSRequestsAuth(
            aws_host=settings.IOT_AWS_HOST,
            aws_region='us-east-1',
            aws_service='execute-api'
        )

        self.session.headers = {'content-type': 'application/json'}
        self.session.auth = aws_auth

    def _get_generic_endpoint_for_metric(self, http_method, endpoint):
        generic_endpoint = re.sub(r'[0-9A-F]{8}-[0-9A-F]{4}-[4][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}',
                                  '<device_id>', endpoint, flags=re.IGNORECASE)

        return f'iot::{http_method}::{generic_endpoint}'

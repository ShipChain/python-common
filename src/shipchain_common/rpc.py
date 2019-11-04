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

import requests
from django.conf import settings
from rest_framework import status
from influxdb_metrics.loader import log_metric, TimingMetric

from .exceptions import RPCError
from .utils import DecimalEncoder

LOG = logging.getLogger('python-common')


class RPCClient:
    def __init__(self):
        self.url = settings.ENGINE_RPC_URL
        self.payload = {"jsonrpc": "2.0", "id": 0, "params": {}}

    def call(self, method, args=None):
        LOG.debug('Calling RPCClient with method %s', method)
        log_metric('python_common.info', tags={'method': 'RPCClient.call', 'module': __name__})

        if args and not isinstance(args, object):
            raise RPCError("Invalid parameter type for Engine RPC call")

        self.payload['method'] = method
        self.payload['params'] = args or {}

        try:
            with TimingMetric('engine_rpc.call', tags={'method': method}) as timer:
                response = settings.REQUESTS_SESSION.post(self.url, data=json.dumps(self.payload, cls=DecimalEncoder),
                                                          timeout=getattr(settings, 'REQUESTS_TIMEOUT', 270))

                LOG.info('rpc_client(%s) duration: %.3f', method, timer.elapsed)

            if status.is_success(response.status_code):
                response_json = response.json()

                if 'error' in response_json:
                    # It's an error properly handled by engine
                    log_metric('engine_rpc.error', tags={'method': method, 'code': response_json['error']['code'],
                                                         'module': __name__})
                    LOG.error('rpc_client(%s) error: %s', method, response_json['error'])
                    raise RPCError(response_json['error']['message'])
            else:
                # It's an unexpected error not handled by engine
                log_metric('engine_rpc.error', tags={'method': method, 'code': response.status_code,
                                                     'module': __name__})
                LOG.error('rpc_client(%s) error: %s', method, response.content)
                raise RPCError(response.content)

        except requests.exceptions.ConnectionError:
            # Don't return the true ConnectionError as it can contain internal URLs
            log_metric('engine_rpc.error', tags={'method': method, 'code': 'ConnectionError', 'module': __name__})
            raise RPCError("Service temporarily unavailable, try again later",
                           status_code=status.HTTP_503_SERVICE_UNAVAILABLE, code='service_unavailable')

        except Exception as exception:
            log_metric('engine_rpc.error', tags={'method': method, 'code': 'Exception', 'module': __name__})
            raise RPCError(str(exception))

        return response_json['result']

    def sign_transaction(self, wallet_id, transaction):
        LOG.debug('Signing transaction %s with wallet_id %s.', transaction, wallet_id)
        log_metric('python_common.info', tags={'method': 'RPCClient.sign_transaction', 'module': __name__})

        result = self.call('transaction.sign', {
            "signerWallet": wallet_id,
            "txUnsigned": transaction
        })

        if 'success' in result and result['success']:
            if 'transaction' in result:
                LOG.debug('Successful signing of transaction.')
                return result['transaction'], result['hash']

        log_metric('engine_rpc.error', tags={'method': 'RPCClient.sign_transaction', 'module': __name__})
        raise RPCError("Invalid response from Engine")

    def send_transaction(self, signed_transaction, callback_url):
        LOG.debug('Sending transaction %s with callback_url %s.', signed_transaction, callback_url)
        log_metric('python_common.info', tags={'method': 'RPCClient.send_transaction', 'module': __name__})

        result = self.call('transaction.send', {
            "callbackUrl": callback_url,
            "txSigned": signed_transaction
        })

        if 'success' in result and result['success']:
            if 'receipt' in result:
                LOG.debug('Successful sending of transaction.')
                return result['receipt']

        log_metric('engine_rpc.error', tags={'method': 'RPCClient.sign_transaction', 'module': __name__})
        raise RPCError("Invalid response from Engine")

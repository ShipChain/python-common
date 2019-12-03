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

from unittest.mock import Mock
from requests.models import Response


def mocked_rpc_response(json, content=None, code=200):
    response = Mock(spec=Response)
    response.status_code = code
    response.content = content
    response.json.return_value = json
    return response


def invalid_eth_amount():
    return mocked_rpc_response({
        "jsonrpc": "2.0",
        "result": {
            "success": True,
            "ether": "1000000",
            "ship": "1000000000000000000"
        },
        "id": 0
    })


def invalid_ship_amount():
    return mocked_rpc_response({
        "jsonrpc": "2.0",
        "result": {
            "success": True,
            "ether": "1000000000000000000",
            "ship": "1000000"
        },
        "id": 0
    })


def mocked_wallet_valid_creation():
    return mocked_rpc_response({
        "jsonrpc": "2.0",
        "result": {
            "success": True,
            "wallet": {
                "id": "d5563423-f040-4e0d-8d87-5e941c748d91",
                "public_key": "a07d45389b1a3b40c6784f749a1d616b4c6f0dba195c0348aef81e9b4c8a7f5c13c0d9b8c360cd2307683a2"
                              "d8f20bd7d801c7a11f4681440f11372f2de465942",
                "address": "0x94Fad76b5Be2b746598BCe12e7b45D7C06D8DA1F"
            }
        },
        "id": 0
    })


def mocked_wallet_invalid_creation():
    return mocked_rpc_response({
        "jsonrpc": "2.0",
        "result": {
            "success": True,
            "wallet": {
                "public_key": "a07d45389b1a3b40c6784f749a1d616b4c6f0dba195c0348aef81e9b4c8a7f5c13c0d9b8c360cd2307683a2"
                              "d8f20bd7d801c7a11f4681440f11372f2de465942",
                "address": "0x94Fad76b5Be2b746598BCe12e7b45D7C06D8DA1F"
            }
        },
        "id": 0
    })


def mocked_wallet_error_creation():
    return mocked_rpc_response({
        "jsonrpc": "2.0",
        "result": {},
        "id": 0
    })


def second_mocked_wallet_valid_creation():
    return mocked_rpc_response({
        "jsonrpc": "2.0",
        "result": {
            "success": True,
            "wallet": {
                "id": "256e621b-2d42-4bf2-ac76-27336d4bf770",
                "public_key": "234111c81a928562e114b9b137dac3c36d7fac5fb6551042608a69c4838335646a641059995510793d9be5f"
                              "c9ea4dd0c5180aafff831462319b3c6878812f987",
                "address": "0x3fB9Ff55672084f3A34E4C77dACF5f3a8D71037a"
            }
        },
        "id": 0
    })


def valid_eth_amount():
    return mocked_rpc_response({
        "jsonrpc": "2.0",
        "result": {
            "success": True,
            "ether": "1000000000000000000",
            "ship": "1000000000000000000"
        },
        "id": 0
    })
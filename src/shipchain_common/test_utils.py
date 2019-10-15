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

import pytz
import re
import random
from datetime import datetime, timedelta
from unittest.mock import Mock
from uuid import UUID

import jwt
from django.conf import settings
from django.test.client import encode_multipart
from requests.models import Response
from rest_framework_simplejwt.utils import aware_utcnow, datetime_to_epoch


def create_form_content(data):
    boundary_string = 'BoUnDaRyStRiNg'

    content = encode_multipart(boundary_string, data)
    content_type = 'multipart/form-data; boundary=' + boundary_string

    return content, content_type


def datetimeAlmostEqual(dt1, dt2=None, ms_threshold=None):
    ms_threshold = settings.MILLISECONDS_THRESHOLD if ms_threshold is None else ms_threshold

    if not dt2:
        dt2 = datetime.now().replace(tzinfo=pytz.UTC)

    return dt1 - timedelta(milliseconds=ms_threshold) <= dt2 <= dt1 + timedelta(milliseconds=ms_threshold)


def get_jwt(exp=None, sub='00000000-0000-0000-0000-000000000000', username='fake@shipchain.io',
            organization_id=None, monthly_rate_limit=None):
    payload = {'email': username, 'username': username, 'sub': sub,
               'aud': '892633'}

    if organization_id:
        payload['organization_id'] = organization_id

    if monthly_rate_limit:
        payload['monthly_rate_limit'] = monthly_rate_limit

    now = aware_utcnow()
    if exp:
        payload['exp'] = exp
    else:
        payload['exp'] = datetime_to_epoch(now + timedelta(minutes=5))

    payload['iat'] = datetime_to_epoch(now)

    return jwt.encode(payload=payload, key=settings.SIMPLE_JWT['PRIVATE_KEY'], algorithm='RS256',
                      headers={'kid': '230498151c214b788dd97f22b85410a5'}).decode('utf-8')


def generate_vnd_json(attributes, object_type, object_id=None):
    """
    Generate Vendor API Json format.  Optionally include `object_id` for PUT/PATCH operations
    """
    data = {
        'data': {
            'type': object_type,
            'attributes': attributes
        }
    }

    if object_id is not None:
        data['data']['id'] = object_id

    return data


def mocked_rpc_response(json, code=200):
    response = Mock(spec=Response)
    response.status_code = code
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


def random_location():
    """
    :return: Randomly generated location geo point.
    """
    return {
        "geometry": {
            "coordinates": [random.uniform(-180, 180), random.uniform(-90, 90)],
            "type": "Point"
        },
        "properties": {
            "source": "Gps",
            "time": random_timestamp(),
            "uncertainty": random.randint(0, 99)
        },
        "type": "Feature"
    }


def random_timestamp():
    """
    Returns a randomly generated datetime timestamp between year 2016 and 2019
    Example: 2017-09-16T19:42:21.7396
    """
    def is_one(a, b):
        value = str(random.randint(a, b))
        if len(value) == 1:
            return '0' + value
        return value

    return f'201{random.randint(6,9)}-{is_one(1,9)}-{is_one(1,30)}T{is_one(0,24)}:{is_one(0,59)}:{is_one(0,59)}.' \
        f'{random.randint(1000,9999)}'


def replace_variables_in_string(string, parameters):
    matches = re.findall(r"<<(\w+?)>>", string)
    for match in matches:
        string = string.replace(f"<<{match}>>", parameters[match])
    return string


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


def validate_uuid4(uuid_string):
    """
    Validate that a UUID string is in fact a valid uuid4.
    Happily, the uuid module does the actual checking for us.
    It is vital that the 'version' kwarg be passed to the UUID() call
    otherwise any 32-character hex string is considered valid.
    """

    try:
        val = UUID(uuid_string, version=4)
    except ValueError:
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        return False

    # If the uuid_string is a valid hex code,
    # but an invalid uuid4,
    # the UUID.__init__ will convert it to a
    # valid uuid4. This is bad for validation purposes.
    return val.hex == uuid_string.replace('-', '')


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


class GeoCoderResponse:
    def __init__(self, status, point=None):
        self.ok = status
        self.xy = point

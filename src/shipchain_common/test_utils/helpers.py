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
from uuid import uuid4

import jwt
from django.conf import settings
from django.test.client import encode_multipart
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


def get_jwt(exp=None, iat=None, sub='00000000-0000-0000-0000-000000000000', username='fake@shipchain.io', **kwargs):
    payload = {'email': username, 'username': username, 'sub': sub,
               'aud': '892633', 'jti': uuid4().hex}

    for prop_name, prop_value in kwargs.items():
        if prop_value is not None:
            # we test 'prop_value' against None to avoid being caught
            # with a boolean 'prop_value = False' which will be false
            # but needs to be set
            payload[prop_name] = prop_value

    now = aware_utcnow()
    if exp:
        payload['exp'] = exp
    else:
        payload['exp'] = datetime_to_epoch(now + timedelta(minutes=5))

    if iat:
        payload['iat'] = iat
    else:
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


class GeoCoderResponse:
    def __init__(self, status, point=None):
        self.ok = status
        self.xy = point

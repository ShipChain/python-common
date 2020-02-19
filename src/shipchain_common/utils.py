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

import decimal
import json
import re
from uuid import UUID
from urllib.parse import parse_qs

from dateutil.parser import parse
from django.db import models
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from enumfields.drf import EnumField
from rest_framework.exceptions import ValidationError


DN_REGEX = re.compile(r'(?:/?)(.+?)(?:=)([^/]+)')


def assertDeepAlmostEqual(test_case, expected, actual, *args, **kwargs):  # nopep8 pylint: disable=invalid-name
    """
    Assert that two complex structures have almost equal contents.

    Compares lists, dicts and tuples recursively. Checks numeric values
    using test_case's :py:meth:`unittest.TestCase.assertAlmostEqual` and
    checks all other values with :py:meth:`unittest.TestCase.assertEqual`.
    Accepts additional positional and keyword arguments and pass those
    intact to assertAlmostEqual() (that's how you specify comparison
    precision).

    :param test_case: TestCase object on which we can call all of the basic
    'assert' methods.
    :type test_case: :py:class:`unittest.TestCase` object
    """
    is_root = '__trace' not in kwargs
    trace = kwargs.pop('__trace', 'ROOT')
    try:
        if isinstance(expected, (int, float, int, complex)):
            test_case.assertAlmostEqual(expected, actual, *args, **kwargs)
        elif isinstance(expected, dict):
            test_case.assertEqual(set(expected), set(actual))
            for key in expected:
                assertDeepAlmostEqual(test_case, expected[key], actual[key],
                                      __trace=repr(key), *args, **kwargs)
        else:
            test_case.assertEqual(expected, actual)
    except AssertionError as exc:
        exc.__dict__.setdefault('traces', []).append(trace)
        if is_root:
            trace = ' -> '.join(reversed(exc.traces))
            exc = AssertionError("%s\nTRACE: %s" % (str(exc), trace))
        raise exc


def _parse_value(item):
    if str(item).lower() in ('true', 'false'):
        # json.loads will parse lowercase booleans
        item = str(item).lower()
    try:
        # We're not actually trying to parse JSON here, but json.loads is a good way to deserialize string values
        parsed = json.loads(item)
    except json.JSONDecodeError:
        parsed = item
    return parsed


def parse_urlencoded_data(data):
    # This function parses urlencoded data, unpacks single-list values, and ensures to parse datatypes for arrays
    body = None
    if data:
        body = {}
        for key, val in parse_qs(data).items():
            if len(val) > 1:
                body[key] = [_parse_value(el) for el in val]
            else:
                body[key] = _parse_value(val[0])
    return body


def build_auth_headers_from_request(request):
    if not request.auth or not isinstance(request.auth, bytes):
        raise Exception("No auth in request")

    token = request.auth.decode('utf-8')
    return {'Authorization': f"JWT {token}"}


def get_client_ip(request):
    """
    Returns ip address from which the http request originated
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        addr = x_forwarded_for.split(',')[0]
    else:
        addr = request.META.get('REMOTE_ADDR')
    return addr


def get_domain_from_email(email):
    if '@' in email:
        domain = email.split("@")[1]
        return domain
    raise ValidationError("Domain can't be determined from username.")


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


def tznow():
    """
    Return an aware or naive datetime.datetime, depending on settings.USE_TZ.
    """
    from django.utils.timezone import now
    return now()


def random_id():
    """
    Cast the UUID to a string
    """
    from uuid import uuid4
    return str(uuid4())


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

    # Check to make sure that the uuid has dashes.
    return str(val) == uuid_string


def remove_dict_key_recursively(dict_obj, list_key_to_remove):
    """
    :param dict_obj: Dictionary object from which we want to remove a particular key
    :param list_key_to_remove: A list of key to remove recursively
    :return: The input dict_obj without the key_to_remove key if found
    """
    keys_to_remove = [key.lower() for key in list_key_to_remove]
    to_return = {}
    for key, value in dict_obj.items():
        if key.lower() not in keys_to_remove:
            if isinstance(value, dict):
                to_return[key] = remove_dict_key_recursively(value, keys_to_remove)
            else:
                to_return[key] = value

    return to_return


def send_templated_email(template, subject, context, recipients, sender=None):
    request = context.get('request', None)
    send_by = sender if sender else settings.DEFAULT_FROM_EMAIL
    email_body = render_to_string(template, context=context, request=request)
    email = EmailMessage(subject, email_body, send_by, recipients)
    email.content_subtype = 'html'
    email.send()


def snake_to_sentence(word):
    return ' '.join(x.capitalize() or '_' for x in word.split('_'))


def parse_dn(ssl_dn):
    return dict(DN_REGEX.findall(ssl_dn))


class AliasField(models.Field):
    def contribute_to_class(self, cls, name, private_only=False):
        """
            virtual_only is deprecated in favor of private_only
        """
        super(AliasField, self).contribute_to_class(cls, name, private_only=True)
        setattr(cls, name, self)

    def __get__(self, instance, instance_type=None):
        return getattr(instance, self.db_column)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):  # pylint: disable=method-hidden
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


class EnumIntegerFieldLabel(EnumField):
    def to_representation(self, instance):
        return str(instance)


class UpperEnumField(EnumField):
    def to_representation(self, instance):
        return super(UpperEnumField, self).to_representation(instance).upper()

# flake8: noqa
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

from .json_asserter import \
    json_asserter, \
    AssertionHelper, \
    JsonAsserterMixin

from .helpers import\
    create_form_content, \
    datetimeAlmostEqual, \
    get_jwt, \
    generate_vnd_json, \
    random_location,\
    random_timestamp, \
    replace_variables_in_string, \
    GeoCoderResponse

from .mocked_rpc_responses import \
    mocked_rpc_response, \
    mocked_wallet_error_creation,\
    mocked_wallet_invalid_creation, \
    mocked_wallet_valid_creation, \
    second_mocked_wallet_valid_creation,\
    invalid_eth_amount, \
    invalid_ship_amount, \
    valid_eth_amount

from .httpretty_asserter import \
    HTTPrettyAsserter, \
    modified_http_pretty

from ..utils import validate_uuid4  # Imported for backwards compatibility usage of `from shipchain_common.test_utils`

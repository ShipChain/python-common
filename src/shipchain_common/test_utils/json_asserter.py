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

import pytest
from rest_framework import status

# pylint: disable=too-many-branches
# pylint: disable=too-many-arguments


class EntityReferenceClass:
    def __init__(self, resource=None, pk=None, attributes=None, relationships=None):
        self.resource = resource
        self.pk = pk
        self.attributes = attributes
        self.relationships = relationships

    def __str__(self):
        return f'Type: {self.resource}; ID: {self.pk}; ' \
               f'attributes: {self.attributes}; relationships: {self.relationships}'


def _vnd_has_error(response_json, error, pointer=None):
    assert 'errors' in response_json, f'Malformed error response: {response_json}'
    errors = response_json['errors']
    assert isinstance(errors, list), f'Error response not a list: {errors}'
    error_found = False

    for single_error in errors:
        if error in single_error['detail']:
            error_found = True
            if pointer:
                found_pointer = single_error['source']['pointer']
                assert pointer in found_pointer, f'Error `{pointer}` not found in {found_pointer}'

    if not error_found:
        assert False, f'Error `{error}` not found in {errors}'


def _json_has_error(errors, error):
    assert isinstance(errors, dict), f'Error response not a dict: {errors}'
    assert 'detail' in errors, f'Malformed error response: {errors}'

    assert errors['detail'] == error, f'Error {error} not found in {errors["detail"]}'


def response_has_error(response, error, pointer=None, vnd=True):
    if error is None:
        return

    response_json = response.json()

    # application/vnd.api+json
    if vnd:
        _vnd_has_error(response_json, error, pointer)

    # application/json
    else:
        _json_has_error(response_json, error)


def _vnd_assert_attributes(response_data, attributes):
    """
    Scan response data for all attributes
    """
    assert 'attributes' in response_data, f'Attributes missing in {response_data}'
    response_attributes = response_data['attributes']

    for key, value in attributes.items():
        assert key in response_attributes, f'Missing Attribute `{key}` in {response_attributes}'
        assert response_attributes[key] == value, f'Attribute Value incorrect `{value}` in {response_attributes}'


def _vnd_assert_entity_ref_in_list(response_list, entity_ref, skip_attributes_property=False):
    found_include = False

    if entity_ref.attributes is None:
        entity_ref.attributes = dict()

    for response_single in response_list:
        if entity_ref.resource and entity_ref.pk:
            if response_single['type'] == entity_ref.resource and response_single['id'] == entity_ref.pk:
                found_include = True
                if skip_attributes_property:
                    break
                for attr_key, attr_value in entity_ref.attributes.items():
                    assert attr_key in response_single['attributes'], \
                        f'List Attribute key `{attr_key}` missing in {response_single}'
                    assert response_single['attributes'][attr_key] == attr_value, \
                        f'List Attribute Value incorrect `{attr_value}` in {response_single}'
                break
        else:
            single_attribute_failed = False

            for attr_key, attr_value in entity_ref.attributes.items():
                if attr_key not in response_single['attributes']:
                    single_attribute_failed = True
                    break
                elif response_single['attributes'][attr_key] != attr_value:
                    single_attribute_failed = True
                    break

            if not single_attribute_failed:
                found_include = True

    assert found_include, f'{entity_ref} NOT IN  {response_list}'


def _vnd_assert_relationships(response_data, relationships):
    """
    Scan response data for all relationships
    """
    assert 'relationships' in response_data, f'Relationships missing in {response_data}'
    response_relationships = response_data['relationships']

    if not isinstance(relationships, list):
        relationships = [relationships]

    for relationship in relationships:
        for relationship_name, relationship_refs in relationship.items():

            assert relationship_name in response_relationships, \
                f'Relationship `{relationship_name}` not in {response_relationships}'

            if not isinstance(relationship_refs, list):
                relationship_refs = [relationship_refs]

            for relationship_ref in relationship_refs:

                assert isinstance(relationship_ref, EntityReferenceClass), \
                    f'asserted relationship is not an EntityRef {relationship_ref}'

                assert 'data' in response_relationships[relationship_name], \
                    f'Data missing in {relationship_name} relationship : {response_relationships[relationship_name]}'

                if isinstance(response_relationships[relationship_name]['data'], list):
                    _vnd_assert_entity_ref_in_list(response_relationships[relationship_name]['data'], relationship_ref,
                                                   skip_attributes_property=True)

                else:
                    if relationship_ref.resource:
                        assert response_relationships[relationship_name]['data']['type'] == relationship_ref.resource, \
                            f'EntityRef resource type `{relationship_ref.resource}` does not match {response_relationships}'
                    if relationship_ref.pk:
                        assert response_relationships[relationship_name]['data']['id'] == relationship_ref.pk, \
                            f'EntityRef ID `{relationship_ref.pk}` does not match {response_relationships}'


def _vnd_assert_include(response, included):
    """
    Scan a response for all included resources
    """
    assert 'included' in response, f'Included missing in {response}'
    response_included = response['included']

    if not isinstance(included, list):
        included = [included]

    for single_include in included:
        assert isinstance(single_include, EntityReferenceClass), \
            f'asserted includes is not an EntityRef {single_include}'
        _vnd_assert_entity_ref_in_list(response_included, single_include)


def _vnd_assertions(response_data, entity_ref):
    if entity_ref.resource:
        assert response_data['type'] == entity_ref.resource, f'Invalid Resource Type in {response_data}'

    if entity_ref.pk:
        assert response_data['id'] == entity_ref.pk, f'Invalid ID in {response_data}'

    if entity_ref.attributes:
        _vnd_assert_attributes(response_data, entity_ref.attributes)

    if entity_ref.relationships:
        _vnd_assert_relationships(response_data, entity_ref.relationships)


def _plain_assert_attributes_in_response(response, attributes):
    for key, value in attributes.items():
        assert key in response, f'Missing Attribute `{key}` in {response}'
        if isinstance(value, dict):
            _plain_assert_attributes_in_response(response[key], value)
        else:
            assert response[key] == value, f'Attribute Value incorrect `{value}` in {response}'


def _plain_assert_attributes_in_list(response_list, attributes):
    found_include = False

    if attributes is None:
        attributes = dict()

    for response_single in response_list:
        single_attribute_failed = False

        try:
            _plain_assert_attributes_in_response(response_single, attributes)
        except AssertionError:
            single_attribute_failed = True

        if not single_attribute_failed:
            found_include = True

    assert found_include, f'{attributes} NOT IN  {response_list}'


def _test_vnd_json(response, entity_refs=None, included=None, is_list=False, count=None, resource=None, pk=None,
                   attributes=None, relationships=None, check_ordering=False):
    assert 'data' in response, f'response does not contain `data` property: {response}'

    # if (attributes or relationships or resource or pk) and entity_refs:
    assert not ((attributes or relationships or resource or pk) and entity_refs), \
        'Use Only `entity_refs` or explicit `attributes`, `relationships`, `resource`, and `pk` but not both'

    if (attributes or relationships or resource or pk) and not entity_refs:
        entity_refs = EntityReferenceClass(resource=resource,
                                           pk=pk,
                                           attributes=attributes,
                                           relationships=relationships)

    response_data = response['data']

    if is_list:
        assert isinstance(response_data, list), f'Response should be a list'

        # Included resources are outside of the list response
        if included:
            _vnd_assert_include(response, included)

        # Assertion for only included and not entities is valid
        if entity_refs:
            if not isinstance(entity_refs, list):
                entity_refs = [entity_refs]

            if not check_ordering:
                for entity_ref in entity_refs:
                    _vnd_assert_entity_ref_in_list(response_data, entity_ref)
            else:
                assert len(entity_refs) <= len(response_data), \
                    f'Error: more entity refs supplied than available in response data. ' \
                    f'{len(response_data)} found asserted {len(entity_refs)}'
                for iteration, entity_ref in enumerate(entity_refs):
                    _vnd_assertions(response_data[iteration], entity_ref)

        if count is not None:
            assert len(response_data) == count, \
                f'Difference in count of response_data, got {len(response_data)} expected {count}'

    else:
        assert not isinstance(response_data, list), f'Response should not be a list'
        assert not (entity_refs and isinstance(entity_refs, list)), \
            f'entity_refs should not be a list for a non-list response'

        assert (count is None), 'Count is only checked when response is list'
        assert not check_ordering, 'Ordering is only checked when response is list'

        # Included resources are outside of the list response
        if included:
            _vnd_assert_include(response, included)

        # Assertion for only status is valid
        if entity_refs:
            _vnd_assertions(response_data, entity_refs)


def _test_regular_json(response, entity_refs=None, included=None, is_list=False, count=None, attributes=None,
                       relationships=None, check_ordering=False):
    assert not relationships, f'relationships not valid when vnd=False'
    assert not entity_refs, f'entity_refs not valid when vnd=False'
    assert not included, f'included not valid when vnd=False'
    assert attributes, f'attributes must be provided when vnd=False'

    if is_list:
        assert isinstance(response, list), f'Response should be a list'

        if not isinstance(attributes, list):
            attributes = [attributes]

        if not check_ordering:
            for attribute in attributes:
                _plain_assert_attributes_in_list(response, attribute)

        else:
            assert len(attributes) <= len(response), \
                f'Error: more attributes supplied than available in response. ' \
                f'{len(attributes)} found asserted {len(response)}'
            for iteration, attribute in enumerate(attributes):
                _plain_assert_attributes_in_response(response[iteration], attribute)
        if count is not None:
            assert len(response) == count,\
                f'Difference in count of response_data, got {len(response)} expected {count}'
    else:
        assert not isinstance(response, list), f'Response should not be a list'
        assert not (attributes and isinstance(attributes, list)), \
            f'attributes should not be a list for a non-list response'

        _plain_assert_attributes_in_response(response, attributes)


def response_has_data(response, vnd=True, entity_refs=None, included=None, is_list=False, count=None,
                      resource=None, pk=None, attributes=None, relationships=None, check_ordering=False):
    response = response.json()

    # application/vnd.api+json
    if vnd:
        _test_vnd_json(response, entity_refs, included, is_list, count, resource, pk, attributes, relationships,
                       check_ordering)

    # application/json
    else:
        _test_regular_json(response, entity_refs, included, is_list, count, attributes, relationships, check_ordering)


def assert_200(response, vnd=True, entity_refs=None, included=None, is_list=False, count=None, check_ordering=False,
               resource=None, pk=None, attributes=None, relationships=None):
    assert response is not None
    assert response.status_code == status.HTTP_200_OK, f'status_code {response.status_code} != 200'
    response_has_data(response,
                      attributes=attributes,
                      relationships=relationships,
                      included=included,
                      is_list=is_list,
                      vnd=vnd,
                      resource=resource,
                      pk=pk,
                      entity_refs=entity_refs,
                      count=count,
                      check_ordering=check_ordering)


def assert_201(response, vnd=True, entity_refs=None, included=None, is_list=False,
               resource=None, pk=None, attributes=None, relationships=None):
    assert response is not None
    assert response.status_code == status.HTTP_201_CREATED, f'status_code {response.status_code} != 201'
    response_has_data(response,
                      attributes=attributes,
                      relationships=relationships,
                      included=included,
                      is_list=is_list,
                      vnd=vnd,
                      resource=resource,
                      pk=pk,
                      entity_refs=entity_refs)


def assert_202(response, vnd=True, entity_refs=None, included=None, is_list=False,
               resource=None, pk=None, attributes=None, relationships=None):
    assert response is not None
    assert response.status_code == status.HTTP_202_ACCEPTED, f'status_code {response.status_code} != 202'
    response_has_data(response,
                      attributes=attributes,
                      relationships=relationships,
                      included=included,
                      is_list=is_list,
                      vnd=vnd,
                      resource=resource,
                      pk=pk,
                      entity_refs=entity_refs)


def assert_204(response):
    assert response is not None
    assert response.status_code == status.HTTP_204_NO_CONTENT, f'status_code {response.status_code} != 204'


def assert_400(response, error=None, pointer=None, vnd=True):
    assert response is not None
    assert response.status_code == status.HTTP_400_BAD_REQUEST, f'status_code {response.status_code} != 400'
    response_has_error(response, error, pointer, vnd)


def assert_401(response, error='Authentication credentials were not provided', vnd=True):
    assert response is not None
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, f'status_code {response.status_code} != 401'
    response_has_error(response, error, vnd=vnd)


def assert_403(response, error='You do not have permission to perform this action', vnd=True):
    assert response is not None
    assert response.status_code == status.HTTP_403_FORBIDDEN, f'status_code {response.status_code} != 403'
    response_has_error(response, error, vnd=vnd)


def assert_404(response, error='Not found', pointer=None, vnd=True):
    assert response is not None
    assert response.status_code == status.HTTP_404_NOT_FOUND, f'status_code {response.status_code} != 404'
    response_has_error(response, error, pointer, vnd)


def assert_405(response, error='Method not allowed', pointer=None, vnd=True):
    assert response is not None
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED, f'status_code {response.status_code} != 405'
    response_has_error(response, error, pointer, vnd)


def assert_500(response, error='A server error occurred.', pointer=None):
    assert response is not None
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR, f'status_code {response.status_code} != 500'
    response_has_error(response, error, pointer)


def assert_503(response, error='Service temporarily unavailable, try again later', pointer=None):
    assert response is not None
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE, f'status_code {response.status_code} != 503'
    response_has_error(response, error, pointer)


class AssertionHelper:
    EntityRef = EntityReferenceClass

    HTTP_200 = assert_200
    HTTP_201 = assert_201
    HTTP_202 = assert_202
    HTTP_204 = assert_204

    HTTP_400 = assert_400
    HTTP_401 = assert_401
    HTTP_403 = assert_403
    HTTP_404 = assert_404
    HTTP_405 = assert_405

    HTTP_500 = assert_500
    HTTP_503 = assert_503


@pytest.fixture(scope='session')
def json_asserter():
    return AssertionHelper


class JsonAsserterMixin:
    @pytest.fixture(autouse=True)
    def set_json_asserter(self, json_asserter):
        self.json_asserter = json_asserter

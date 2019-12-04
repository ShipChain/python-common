from unittest.mock import Mock

import pytest

from rest_framework import status
from shipchain_common.test_utils import AssertionHelper

EXAMPLE_PLAIN = {
    'id': '07b374c3-ed9b-4811-901a-d0c5d746f16a',
    'name': 'example 1',
    'field_1': 1,
    'owner': {
        'username': 'user1'
    }
}

EXAMPLE_USER = {
    'type': 'User',
    'id': '07b374c3-ed9b-4811-901a-d0c5d746f16a',
    'attributes': {
        'username': 'user1'
    }
}

EXAMPLE_RESOURCE = {
    'type': 'ExampleResource',
    'id': 'a6f554e9-3bd3-4972-90e1-b8a19aab7091',
    'attributes': {
        'name': 'example 1',
        'field_1': 1
    }
}

EXAMPLE_RESOURCE_2 = {
    'type': 'ExampleResource',
    'id': 'b717eff3-b021-4f3f-a2be-7cdc08a1bfb5',
    'attributes': {
        'name': 'example 2',
        'field_1': 2
    }
}

EXAMPLE_RESOURCE_3 = {
    'type': 'ExampleResource',
    'id': 'd72d5d56-c359-455e-876b-52835228c852',
    'attributes': {
        'name': 'example 3',
        'field_1': 3
    }
}


class TestAssertionHelper:

    @pytest.fixture(scope='session')
    def assertions(self):
        return AssertionHelper

    @pytest.fixture(autouse=True)
    def make_build_response(self):
        def _build_response(data, status_code=status.HTTP_200_OK):
            return Mock(status_code=status_code, json=lambda: data)
        self.build_response = _build_response

    @pytest.fixture
    def vnd_single(self):
        return {
            'data': {
                    'type': EXAMPLE_RESOURCE['type'],
                    'id': EXAMPLE_RESOURCE['id'],
                    'attributes': EXAMPLE_RESOURCE['attributes'],
                    'relationships': {
                        'owner': {
                            'data': {
                                'type': EXAMPLE_USER['type'],
                                'id': EXAMPLE_USER['id']
                            }
                        },
                        'children': {
                            'meta': {
                                'count': 1
                            },
                            'data': [
                                {
                                    'type': EXAMPLE_RESOURCE_2['type'],
                                    'id': EXAMPLE_RESOURCE_2['id']
                                }
                            ]
                        }
                    }
                },
            'included': [
                EXAMPLE_USER,
                EXAMPLE_RESOURCE_2
            ]
        }

    @pytest.fixture
    def vnd_list(self):
        return {
            'data': [
                {
                    'type': EXAMPLE_RESOURCE['type'],
                    'id': EXAMPLE_RESOURCE['id'],
                    'attributes': EXAMPLE_RESOURCE['attributes'],
                    'relationships': {
                        'owner': {
                            'data': {
                                'type': EXAMPLE_USER['type'],
                                'id': EXAMPLE_USER['id']
                            }
                        },
                        'children': {
                            'meta': {
                                'count': 1
                            },
                            'data': [
                                {
                                    'type': EXAMPLE_RESOURCE_2['type'],
                                    'id': EXAMPLE_RESOURCE_2['id']
                                }
                            ]
                        }
                    }
                },
                {
                    'type': EXAMPLE_RESOURCE_3['type'],
                    'id': EXAMPLE_RESOURCE_3['id'],
                    'attributes': EXAMPLE_RESOURCE_3['attributes'],
                    'relationships': {
                        'owner': {
                            'data': {
                                'type': EXAMPLE_USER['type'],
                                'id': EXAMPLE_USER['id']
                            }
                        },
                        'children': {
                            'meta': {
                                'count': 1
                            },
                            'data': [
                                {
                                    'type': EXAMPLE_RESOURCE_2['type'],
                                    'id': EXAMPLE_RESOURCE_2['id']
                                }
                            ]
                        }
                    }
                },
            ],
            'included': [
                EXAMPLE_USER,
                EXAMPLE_RESOURCE_2
            ]
        }

    @pytest.fixture
    def vnd_error(self):
        return {
            'errors': [
                {
                    'detail': ''
                }
            ]
        }

    @pytest.fixture
    def vnd_error_400(self, vnd_error):
        vnd_error['errors'][0]['detail'] = 'generic 400 error'
        return vnd_error

    @pytest.fixture
    def vnd_error_401(self, vnd_error):
        vnd_error['errors'][0]['detail'] = 'Authentication credentials were not provided'
        return vnd_error

    @pytest.fixture
    def vnd_error_403(self, vnd_error):
        vnd_error['errors'][0]['detail'] = 'You do not have permission to perform this action'
        return vnd_error

    @pytest.fixture
    def vnd_error_404(self, vnd_error):
        vnd_error['errors'][0]['detail'] = 'Not found'
        return vnd_error

    def test_status_200(self, assertions, vnd_single, vnd_error_400):
        response = self.build_response(vnd_single)
        assertions.HTTP_200(response)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_error_400, status_code=status.HTTP_400_BAD_REQUEST)
            assertions.HTTP_200(response)
        assert 'status_code 400 != 200' in str(err.value)

    def test_status_201(self, assertions, vnd_single, vnd_error_400):
        response = self.build_response(vnd_single, status_code=status.HTTP_201_CREATED)
        assertions.HTTP_201(response)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_error_400, status_code=status.HTTP_400_BAD_REQUEST)
            assertions.HTTP_201(response)
        assert 'status_code 400 != 201' in str(err.value)

    def test_status_204(self, assertions, vnd_single, vnd_error_400):
        response = self.build_response(vnd_single, status_code=status.HTTP_204_NO_CONTENT)
        assertions.HTTP_204(response)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_error_400, status_code=status.HTTP_400_BAD_REQUEST)
            assertions.HTTP_204(response)
        assert 'status_code 400 != 204' in str(err.value)

    def test_status_400(self, assertions, vnd_single, vnd_error_400):
        response = self.build_response(vnd_error_400, status_code=status.HTTP_400_BAD_REQUEST)
        assertions.HTTP_400(response)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_single)
            assertions.HTTP_400(response)
        assert 'status_code 200 != 400' in str(err.value)

    def test_status_400_custom_message(self, assertions, vnd_single, vnd_error_400):
        vnd_error_400['errors'][0]['detail'] = 'custom error message'
        response = self.build_response(vnd_error_400, status_code=status.HTTP_400_BAD_REQUEST)
        assertions.HTTP_400(response, error='custom error message')

    def test_status_401(self, assertions, vnd_single, vnd_error_401):
        response = self.build_response(vnd_error_401, status_code=status.HTTP_401_UNAUTHORIZED)
        assertions.HTTP_401(response)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_single)
            assertions.HTTP_401(response)
        assert 'status_code 200 != 401' in str(err.value)

    def test_status_403(self, assertions, vnd_single, vnd_error_403):
        response = self.build_response(vnd_error_403, status_code=status.HTTP_403_FORBIDDEN)
        assertions.HTTP_403(response)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_single)
            assertions.HTTP_403(response)
        assert 'status_code 200 != 403' in str(err.value)

    def test_status_404(self, assertions, vnd_single, vnd_error_404):
        response = self.build_response(vnd_error_404, status_code=status.HTTP_404_NOT_FOUND)
        assertions.HTTP_404(response)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_single)
            assertions.HTTP_404(response)
        assert 'status_code 200 != 404' in str(err.value)

    def test_status_wrong_message(self, assertions, vnd_single, vnd_error_404):
        response = self.build_response(vnd_error_404, status_code=status.HTTP_404_NOT_FOUND)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_404(response, error='Not the correct error')
        assert f'Error `Not the correct error` not found in' in str(err.value)

    def test_exclusive_entity_refs_or_fields(self, assertions, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, entity_refs=assertions.EntityRef(), attributes={'test': 1})
        assert 'Use Only `entity_refs` or explicit `attributes`, `relationships`, `resource`, and `pk` but not both' \
               in str(err.value)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, entity_refs=assertions.EntityRef(), relationships={'test': 1})
        assert 'Use Only `entity_refs` or explicit `attributes`, `relationships`, `resource`, and `pk` but not both' \
               in str(err.value)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, entity_refs=assertions.EntityRef(), resource='test')
        assert 'Use Only `entity_refs` or explicit `attributes`, `relationships`, `resource`, and `pk` but not both' \
               in str(err.value)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, entity_refs=assertions.EntityRef(), pk='test')
        assert 'Use Only `entity_refs` or explicit `attributes`, `relationships`, `resource`, and `pk` but not both' \
               in str(err.value)

    def test_vnd_with_non_jsonapi_data(self, assertions):
        response = self.build_response(EXAMPLE_PLAIN)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, attributes=EXAMPLE_PLAIN)
        assert f'response does not contain `data` property' in str(err.value)

    def test_vnd_is_list(self, assertions, vnd_single, vnd_list):
        single_response = self.build_response(vnd_single)
        list_response = self.build_response(vnd_list)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(single_response, is_list=True)
        assert 'Response should be a list' in str(err.value)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(list_response)
        assert 'Response should not be a list' in str(err.value)

    def test_vnd_attributes_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)
        assertions.HTTP_200(response, attributes=EXAMPLE_RESOURCE['attributes'])

    def test_vnd_attributes_not_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, attributes=EXAMPLE_RESOURCE_2['attributes'])
        assert f'Attribute Value incorrect `{EXAMPLE_RESOURCE_2["attributes"]["name"]}` in ' in str(err.value)

    def test_vnd_relationships_should_be_entity_ref(self, assertions, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, relationships={'owner': EXAMPLE_RESOURCE_2})
        assert f'asserted relationship is not an EntityRef' in str(err.value)

    def test_vnd_relationships_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)

        assertions.HTTP_200(response, relationships={'owner': assertions.EntityRef(
            resource=EXAMPLE_USER['type'],
            pk=EXAMPLE_USER['id'],
        )})

    def test_vnd_relationships_not_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, relationships={'owner': assertions.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                pk=EXAMPLE_RESOURCE['id'],
            )})
        assert f'EntityRef resource type `{EXAMPLE_RESOURCE["type"]}` does not match' in str(err.value)

    def test_vnd_included_should_be_entity_ref(self, assertions, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, included=EXAMPLE_RESOURCE_2)
        assert f'asserted includes is not an EntityRef' in str(err.value)

    def test_vnd_included_full_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)

        assertions.HTTP_200(response, included=assertions.EntityRef(
            resource=EXAMPLE_RESOURCE_2['type'],
            pk=EXAMPLE_RESOURCE_2['id'],
            attributes=EXAMPLE_RESOURCE_2['attributes'],
        ))

    def test_vnd_included_full_not_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)
        include = assertions.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                pk=EXAMPLE_RESOURCE['id'],
                attributes=EXAMPLE_RESOURCE['attributes'],
            )

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, included=include)
        assert f'{include} NOT IN' in str(err.value)

    def test_vnd_included_type_pk_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)

        assertions.HTTP_200(response, included=assertions.EntityRef(
            resource=EXAMPLE_RESOURCE_2['type'],
            pk=EXAMPLE_RESOURCE_2['id'],
        ))

    def test_vnd_included_type_pk_not_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)
        include = assertions.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                pk=EXAMPLE_RESOURCE['id'],
            )

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, included=include)
        assert f'{include} NOT IN' in str(err.value)

    def test_vnd_included_attributes_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)

        assertions.HTTP_200(response, included=assertions.EntityRef(
            attributes=EXAMPLE_RESOURCE_2['attributes'],
        ))

    def test_vnd_included_attributes_not_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)
        include = assertions.EntityRef(
                attributes=EXAMPLE_RESOURCE['attributes'],
            )

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, included=include)
        assert f'{include} NOT IN' in str(err.value)

    def test_vnd_included_list_all_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)

        assertions.HTTP_200(response, included=[
            assertions.EntityRef(
                resource=EXAMPLE_RESOURCE_2['type'],
                pk=EXAMPLE_RESOURCE_2['id'],
                attributes=EXAMPLE_RESOURCE_2['attributes']),
            assertions.EntityRef(
                resource=EXAMPLE_USER['type'],
                pk=EXAMPLE_USER['id'],
                attributes=EXAMPLE_USER['attributes']),
            ])

    def test_vnd_included_list_one_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)
        include_1 = assertions.EntityRef(
            resource=EXAMPLE_RESOURCE['type'],
            pk=EXAMPLE_RESOURCE['id'],
            attributes=EXAMPLE_RESOURCE['attributes'])
        include_2 = assertions.EntityRef(
            resource=EXAMPLE_USER['type'],
            pk=EXAMPLE_USER['id'],
            attributes=EXAMPLE_USER['attributes'])

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, included=[include_1, include_2])
        assert f'{include_1} NOT IN' in str(err.value)

    def test_vnd_included_list_none_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)
        include_1 = assertions.EntityRef(
            resource=EXAMPLE_RESOURCE['type'],
            pk=EXAMPLE_RESOURCE['id'],
            attributes=EXAMPLE_RESOURCE['attributes'])
        include_2 = assertions.EntityRef(
            resource=EXAMPLE_RESOURCE_3['type'],
            pk=EXAMPLE_RESOURCE_3['id'],
            attributes=EXAMPLE_RESOURCE_3['attributes'])

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, included=[include_1, include_2])
        assert f'{include_1} NOT IN' in str(err.value)

    def test_entity_list_non_list_response(self, assertions, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, entity_refs=[assertions.EntityRef()])
        assert 'entity_refs should not be a list for a non-list response' in str(err.value)

    def test_vnd_entity_full_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)
        assertions.HTTP_200(response, entity_refs=assertions.EntityRef(
            resource=EXAMPLE_RESOURCE['type'],
            pk=EXAMPLE_RESOURCE['id'],
            attributes=EXAMPLE_RESOURCE['attributes'],
            relationships={'owner': assertions.EntityRef(
                resource=EXAMPLE_USER['type'],
                pk=EXAMPLE_USER['id'],
            )}
        ))

    def test_vnd_entity_full_type_not_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, entity_refs=assertions.EntityRef(
                resource=EXAMPLE_USER['type'],
                pk=EXAMPLE_RESOURCE['id'],
                attributes=EXAMPLE_RESOURCE['attributes'],
                relationships={'owner': assertions.EntityRef(
                    resource=EXAMPLE_USER['type'],
                    pk=EXAMPLE_USER['id'],
                )}
            ))
        assert f'Invalid Resource Type in' in str(err.value)

    def test_vnd_entity_full_id_not_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, entity_refs=assertions.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                pk=EXAMPLE_USER['id'],
                attributes=EXAMPLE_RESOURCE['attributes'],
                relationships={'owner': assertions.EntityRef(
                    resource=EXAMPLE_USER['type'],
                    pk=EXAMPLE_USER['id'],
                )}
            ))
        assert f'Invalid ID in' in str(err.value)

    def test_vnd_entity_full_attributes_missing(self, assertions, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, entity_refs=assertions.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                pk=EXAMPLE_RESOURCE['id'],
                attributes=EXAMPLE_USER['attributes'],
                relationships={'owner': assertions.EntityRef(
                    resource=EXAMPLE_USER['type'],
                    pk=EXAMPLE_USER['id'],
                )}
            ))
        assert f'Missing Attribute `username` in' in str(err.value)

    def test_vnd_entity_full_attributes_not_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, entity_refs=assertions.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                pk=EXAMPLE_RESOURCE['id'],
                attributes=EXAMPLE_RESOURCE_2['attributes'],
                relationships={'owner': assertions.EntityRef(
                    resource=EXAMPLE_USER['type'],
                    pk=EXAMPLE_USER['id'],
                )}
            ))
        assert f'Attribute Value incorrect `example 2` in' in str(err.value)

    def test_vnd_entity_full_relationships_type_not_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, entity_refs=assertions.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                pk=EXAMPLE_RESOURCE['id'],
                attributes=EXAMPLE_RESOURCE['attributes'],
                relationships={'owner': assertions.EntityRef(
                    resource=EXAMPLE_RESOURCE['type'],
                    pk=EXAMPLE_USER['id'],
                )}
            ))
        assert f'EntityRef resource type `{EXAMPLE_RESOURCE["type"]}` does not match' in str(err.value)

    def test_vnd_entity_full_relationships_pk_not_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, entity_refs=assertions.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                pk=EXAMPLE_RESOURCE['id'],
                attributes=EXAMPLE_RESOURCE['attributes'],
                relationships={'owner': assertions.EntityRef(
                    resource=EXAMPLE_USER['type'],
                    pk=EXAMPLE_RESOURCE['id'],
                )}
            ))
        assert f'EntityRef ID `{EXAMPLE_RESOURCE["id"]}` does not match' in str(err.value)

    def test_vnd_entity_type_pk_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)
        assertions.HTTP_200(response, entity_refs=assertions.EntityRef(
            resource=EXAMPLE_RESOURCE['type'],
            pk=EXAMPLE_RESOURCE['id'],
        ))

    def test_vnd_entity_type_pk_not_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)
        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, entity_refs=assertions.EntityRef(
                resource=EXAMPLE_USER['type'],
                pk=EXAMPLE_RESOURCE['id'],
            ))
        assert f'Invalid Resource Type in' in str(err.value)

    def test_vnd_entity_attribute_only_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)
        assertions.HTTP_200(response, entity_refs=assertions.EntityRef(
            attributes=EXAMPLE_RESOURCE['attributes']
        ))

    def test_vnd_entity_attribute_only_not_match(self, assertions, vnd_single):
        response = self.build_response(vnd_single)
        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, entity_refs=assertions.EntityRef(
                attributes=EXAMPLE_RESOURCE_2['attributes'],
            ))
        assert f'Attribute Value incorrect `example 2` in' in str(err.value)

    def test_vnd_list_entity_full_match(self, assertions, vnd_list):
        response = self.build_response(vnd_list)
        assertions.HTTP_200(response, is_list=True, entity_refs=assertions.EntityRef(
            resource=EXAMPLE_RESOURCE['type'],
            pk=EXAMPLE_RESOURCE['id'],
            attributes=EXAMPLE_RESOURCE['attributes'],
            relationships={'owner': assertions.EntityRef(
                resource=EXAMPLE_USER['type'],
                pk=EXAMPLE_USER['id'],
            )}
        ))

    def test_vnd_list_entity_list_all_match(self, assertions, vnd_list):
        response = self.build_response(vnd_list)
        entity_1 = assertions.EntityRef(
            resource=EXAMPLE_RESOURCE['type'],
            pk=EXAMPLE_RESOURCE['id'],
            attributes=EXAMPLE_RESOURCE['attributes'],
            relationships={'owner': assertions.EntityRef(
                resource=EXAMPLE_USER['type'],
                pk=EXAMPLE_USER['id'],
            )})
        entity_2 = assertions.EntityRef(
            resource=EXAMPLE_RESOURCE_3['type'],
            pk=EXAMPLE_RESOURCE_3['id'],
            attributes=EXAMPLE_RESOURCE_3['attributes'],
            relationships={'owner': assertions.EntityRef(
                resource=EXAMPLE_USER['type'],
                pk=EXAMPLE_USER['id'],
            )})
        assertions.HTTP_200(response, is_list=True, entity_refs=[entity_1, entity_2])

    def test_vnd_list_entity_list_one_not_match(self, assertions, vnd_list):
        response = self.build_response(vnd_list)
        entity_1 = assertions.EntityRef(
            resource=EXAMPLE_RESOURCE['type'],
            pk=EXAMPLE_RESOURCE['id'],
            attributes=EXAMPLE_RESOURCE['attributes'],
            relationships={'owner': assertions.EntityRef(
                resource=EXAMPLE_USER['type'],
                pk=EXAMPLE_USER['id'],
            )})
        entity_2 = assertions.EntityRef(
            resource=EXAMPLE_RESOURCE_3['type'],
            pk=EXAMPLE_RESOURCE_2['id'],
            attributes=EXAMPLE_RESOURCE_3['attributes'],
            relationships={'owner': assertions.EntityRef(
                resource=EXAMPLE_USER['type'],
                pk=EXAMPLE_USER['id'],
            )})

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, is_list=True, entity_refs=[entity_1, entity_2])
        assert f'{entity_2} NOT IN' in str(err.value)

    def test_plain_json_valid_parameters(self, assertions):
        response = self.build_response(EXAMPLE_PLAIN)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, vnd=False, entity_refs={assertions.EntityRef()})
        assert f'entity_refs not valid when vnd=False' in str(err.value)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, vnd=False, relationships=assertions.EntityRef())
        assert f'relationships not valid when vnd=False' in str(err.value)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, vnd=False, included=assertions.EntityRef())
        assert f'included not valid when vnd=False' in str(err.value)

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, vnd=False)
        assert f'attributes must be provided when vnd=False' in str(err.value)

    def test_plain_json_attributes(self, assertions):
        response = self.build_response(EXAMPLE_PLAIN)

        assertions.HTTP_200(response, vnd=False, attributes=EXAMPLE_PLAIN)

    def test_plain_json_attributes_top_level_missing(self, assertions):
        response = self.build_response(EXAMPLE_PLAIN)

        invalid_attributes = EXAMPLE_PLAIN.copy()
        invalid_attributes['new_field'] = 1

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, vnd=False, attributes=invalid_attributes)
        assert f'Missing Attribute `new_field` in ' in str(err.value)

    def test_plain_json_attributes_top_level_mismatch(self, assertions):
        response = self.build_response(EXAMPLE_PLAIN)

        invalid_attributes = EXAMPLE_PLAIN.copy()
        invalid_attributes['id'] = 1

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, vnd=False, attributes=invalid_attributes)
        assert f'Attribute Value incorrect `1` in ' in str(err.value)

    def test_plain_json_attributes_nested_missing(self, assertions):
        response = self.build_response(EXAMPLE_PLAIN)

        invalid_attributes = EXAMPLE_PLAIN.copy()
        invalid_attributes['owner'] = EXAMPLE_PLAIN['owner'].copy()
        invalid_attributes['owner']['new_field'] = 'test'

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, vnd=False, attributes=invalid_attributes)
        assert f'Missing Attribute `new_field` in ' in str(err.value)

    def test_plain_json_attributes_nested_mismatch(self, assertions):
        response = self.build_response(EXAMPLE_PLAIN)

        invalid_attributes = EXAMPLE_PLAIN.copy()
        invalid_attributes['owner'] = EXAMPLE_PLAIN['owner'].copy()
        invalid_attributes['owner']['id'] = 'test'

        with pytest.raises(AssertionError) as err:
            assertions.HTTP_200(response, vnd=False, attributes=invalid_attributes)
        assert f'Missing Attribute `id` in ' in str(err.value)

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

EXAMPLE_PLAIN_2 = {
    'id': 'bf0d0b89-482f-40dd-b29b-9e5e05b83ed6',
    'name': 'example 2',
    'field_1': 2,
    'owner': {
        'username': 'user2'
    }
}

EXAMPLE_PLAIN_3 = {
    'id': '2aa1db84-6618-4e35-9b2a-f450c20699fe',
    'name': 'example 3',
    'field_1': 3,
    'owner': {
        'username': 'user3'
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

EXAMPLE_RESOURCE_4 = {
    'type': 'ExampleResource',
    'id': 'e8ba3cd9-9b5e-41fa-9b08-116284e968fd',
    'attributes': {
        'name': 'example 4',
        'field_1': 4
    }
}


@pytest.fixture
def vnd_single():
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
                        'count': 2
                    },
                    'data': [
                        {
                            'type': EXAMPLE_RESOURCE_2['type'],
                            'id': EXAMPLE_RESOURCE_2['id']
                        },
                        {
                            'type': EXAMPLE_RESOURCE_4['type'],
                            'id': EXAMPLE_RESOURCE_4['id']
                        }
                    ]
                }
            },
            'meta': {
                'key': 'value',
                'other_key': 'other_value',
            }
        },
        'included': [
            EXAMPLE_USER,
            EXAMPLE_RESOURCE_2,
            EXAMPLE_RESOURCE_4
        ]
    }


@pytest.fixture
def vnd_list():
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
def vnd_error():
    return {
        'errors': [
            {
                'detail': ''
            }
        ]
    }


@pytest.fixture
def vnd_error_400(vnd_error):
    vnd_error['errors'][0]['detail'] = 'generic 400 error'
    vnd_error['errors'][0]['source'] = {
        'pointer': ''
    }
    return vnd_error


@pytest.fixture
def json_error():
    return {
        'detail': 'Error detail'
    }


@pytest.fixture
def entity_ref_1():
    return AssertionHelper.EntityRef(
        resource=EXAMPLE_RESOURCE['type'],
        pk=EXAMPLE_RESOURCE['id'],
        attributes=EXAMPLE_RESOURCE['attributes'],
        relationships={'owner': AssertionHelper.EntityRef(
            resource=EXAMPLE_USER['type'],
            pk=EXAMPLE_USER['id'],
        )})


@pytest.fixture
def entity_ref_3():
    return AssertionHelper.EntityRef(
        resource=EXAMPLE_RESOURCE_3['type'],
        pk=EXAMPLE_RESOURCE_3['id'],
        attributes=EXAMPLE_RESOURCE_3['attributes'],
        relationships={'owner': AssertionHelper.EntityRef(
            resource=EXAMPLE_USER['type'],
            pk=EXAMPLE_USER['id'],
        )})


class TestAssertionHelper:
    @pytest.fixture(autouse=True)
    def make_build_response(self):
        def _build_response(data, status_code=status.HTTP_200_OK):
            return Mock(status_code=status_code, json=lambda: data)

        self.build_response = _build_response

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

    @pytest.fixture
    def vnd_error_405(self, vnd_error):
        vnd_error['errors'][0]['detail'] = 'Method not allowed'
        return vnd_error

    def test_status_200(self, vnd_single, vnd_error_400):
        response = self.build_response(vnd_single)
        AssertionHelper.HTTP_200(response)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_error_400, status_code=status.HTTP_400_BAD_REQUEST)
            AssertionHelper.HTTP_200(response)
        assert 'status_code 400 != 200' in str(err.value)

    def test_status_201(self, vnd_single, vnd_error_400):
        response = self.build_response(vnd_single, status_code=status.HTTP_201_CREATED)
        AssertionHelper.HTTP_201(response)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_error_400, status_code=status.HTTP_400_BAD_REQUEST)
            AssertionHelper.HTTP_201(response)
        assert 'status_code 400 != 201' in str(err.value)

    def test_status_202(self, vnd_single, vnd_error_400):
        response = self.build_response(vnd_single, status_code=status.HTTP_202_ACCEPTED)
        AssertionHelper.HTTP_202(response)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_error_400, status_code=status.HTTP_400_BAD_REQUEST)
            AssertionHelper.HTTP_202(response)
        assert 'status_code 400 != 202' in str(err.value)

    def test_status_204(self, vnd_single, vnd_error_400):
        response = self.build_response(vnd_single, status_code=status.HTTP_204_NO_CONTENT)
        AssertionHelper.HTTP_204(response)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_error_400, status_code=status.HTTP_400_BAD_REQUEST)
            AssertionHelper.HTTP_204(response)
        assert 'status_code 400 != 204' in str(err.value)

    def test_status_400(self, vnd_single, vnd_error_400):
        response = self.build_response(vnd_error_400, status_code=status.HTTP_400_BAD_REQUEST)
        AssertionHelper.HTTP_400(response)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_single)
            AssertionHelper.HTTP_400(response)
        assert 'status_code 200 != 400' in str(err.value)

    def test_status_400_custom_message(self, vnd_error_400):
        vnd_error_400['errors'][0]['detail'] = 'custom error message'
        response = self.build_response(vnd_error_400, status_code=status.HTTP_400_BAD_REQUEST)
        AssertionHelper.HTTP_400(response, error='custom error message')

    def test_status_400_custom_pointer(self, vnd_error_400):
        vnd_error_400['errors'][0]['detail'] = 'custom error message'
        vnd_error_400['errors'][0]['source']['pointer'] = 'pointer'
        response = self.build_response(vnd_error_400, status_code=status.HTTP_400_BAD_REQUEST)
        AssertionHelper.HTTP_400(response, error='custom error message', pointer='pointer')

    def test_status_400_json(self, vnd_single, json_error):
        response = self.build_response(json_error, status_code=status.HTTP_400_BAD_REQUEST)
        AssertionHelper.HTTP_400(response, error=json_error['detail'], vnd=False)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(json_error, status_code=status.HTTP_200_OK)
            AssertionHelper.HTTP_400(response, error='Different error', vnd=False)
        assert 'status_code 200 != 400' in str(err.value)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(json_error, status_code=status.HTTP_400_BAD_REQUEST)
            AssertionHelper.HTTP_400(response, error='Different error', vnd=False)
        assert f'Error Different error not found in {json_error["detail"]}' in str(err.value)

    def test_status_401(self, vnd_single, vnd_error_401):
        response = self.build_response(vnd_error_401, status_code=status.HTTP_401_UNAUTHORIZED)
        AssertionHelper.HTTP_401(response)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_single)
            AssertionHelper.HTTP_401(response)
        assert 'status_code 200 != 401' in str(err.value)

    def test_status_401_json(self, vnd_single, json_error):
        response = self.build_response(json_error, status_code=status.HTTP_401_UNAUTHORIZED)
        AssertionHelper.HTTP_401(response, error=json_error['detail'], vnd=False)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(json_error, status_code=status.HTTP_200_OK)
            AssertionHelper.HTTP_401(response, error='Different error', vnd=False)
        assert 'status_code 200 != 401' in str(err.value)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(json_error, status_code=status.HTTP_401_UNAUTHORIZED)
            AssertionHelper.HTTP_401(response, error='Different error', vnd=False)
        assert f'Error Different error not found in {json_error["detail"]}' in str(err.value)

    def test_status_403(self, vnd_single, vnd_error_403):
        response = self.build_response(vnd_error_403, status_code=status.HTTP_403_FORBIDDEN)
        AssertionHelper.HTTP_403(response)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_single)
            AssertionHelper.HTTP_403(response)
        assert 'status_code 200 != 403' in str(err.value)

    def test_status_403_json(self, vnd_single, json_error):
        response = self.build_response(json_error, status_code=status.HTTP_403_FORBIDDEN)
        AssertionHelper.HTTP_403(response, error=json_error['detail'], vnd=False)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(json_error, status_code=status.HTTP_200_OK)
            AssertionHelper.HTTP_403(response, error='Different error', vnd=False)
        assert 'status_code 200 != 403' in str(err.value)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(json_error, status_code=status.HTTP_403_FORBIDDEN)
            AssertionHelper.HTTP_403(response, error='Different error', vnd=False)
        assert f'Error Different error not found in {json_error["detail"]}' in str(err.value)

    def test_status_404(self, vnd_single, vnd_error_404):
        response = self.build_response(vnd_error_404, status_code=status.HTTP_404_NOT_FOUND)
        AssertionHelper.HTTP_404(response)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_single)
            AssertionHelper.HTTP_404(response)
        assert 'status_code 200 != 404' in str(err.value)

    def test_status_404_json(self, vnd_single, json_error):
        response = self.build_response(json_error, status_code=status.HTTP_404_NOT_FOUND)
        AssertionHelper.HTTP_404(response, error=json_error['detail'], vnd=False)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(json_error, status_code=status.HTTP_200_OK)
            AssertionHelper.HTTP_404(response, error='Different error', vnd=False)
        assert 'status_code 200 != 404' in str(err.value)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(json_error, status_code=status.HTTP_404_NOT_FOUND)
            AssertionHelper.HTTP_404(response, error='Different error', vnd=False)
        assert f'Error Different error not found in {json_error["detail"]}' in str(err.value)

    def test_status_405(self, vnd_single, vnd_error_405):
        response = self.build_response(vnd_error_405, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
        AssertionHelper.HTTP_405(response, error='Method not allowed')

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_single)
            AssertionHelper.HTTP_405(response, error='Method not allowed')
        assert 'status_code 200 != 405' in str(err.value)

    def test_status_405_json(self, vnd_single, json_error):
        response = self.build_response(json_error, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
        AssertionHelper.HTTP_405(response, error=json_error['detail'], vnd=False)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(json_error, status_code=status.HTTP_200_OK)
            AssertionHelper.HTTP_405(response, error='Different error', vnd=False)
        assert 'status_code 200 != 405' in str(err.value)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(json_error, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
            AssertionHelper.HTTP_405(response, error='Different error', vnd=False)
        assert f'Error Different error not found in {json_error["detail"]}' in str(err.value)

    def test_status_500(self, vnd_single, vnd_error):
        vnd_error['errors'][0]['detail'] = 'A server error occurred.'
        response = self.build_response(vnd_error, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        AssertionHelper.HTTP_500(response)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_single)
            AssertionHelper.HTTP_500(response)
        assert 'status_code 200 != 500' in str(err.value)

    def test_status_500_custom_message(self, vnd_error):
        vnd_error['errors'][0]['detail'] = 'custom error message'
        response = self.build_response(vnd_error, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        AssertionHelper.HTTP_500(response, error='custom error message')

    def test_status_503(self, vnd_single, vnd_error):
        vnd_error['errors'][0]['detail'] = 'Service temporarily unavailable, try again later'
        response = self.build_response(vnd_error, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        AssertionHelper.HTTP_503(response)

        with pytest.raises(AssertionError) as err:
            response = self.build_response(vnd_single)
            AssertionHelper.HTTP_503(response)
        assert 'status_code 200 != 503' in str(err.value)

    def test_status_503_custom_message(self, vnd_error):
        vnd_error['errors'][0]['detail'] = 'custom error message'
        response = self.build_response(vnd_error, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        AssertionHelper.HTTP_503(response, error='custom error message')

    def test_status_wrong_message(self, vnd_error_404):
        response = self.build_response(vnd_error_404, status_code=status.HTTP_404_NOT_FOUND)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_404(response, error='Not the correct error')
        assert f'Error `Not the correct error` not found in' in str(err.value)

    def test_status_400_wrong_pointer(self, vnd_error_400):
        vnd_error_400['errors'][0]['detail'] = 'custom error message'
        vnd_error_400['errors'][0]['source']['pointer'] = 'pointer'
        response = self.build_response(vnd_error_400, status_code=status.HTTP_400_BAD_REQUEST)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_400(response, error='custom error message', pointer='Not the correct pointer')
        assert f'Error `Not the correct pointer` not found in' in str(err.value)

    def test_status_404_wrong_pointer(self, vnd_error):
        vnd_error['errors'][0]['detail'] = 'Not found'
        vnd_error['errors'][0]['source'] = {
            'pointer': 'correct pointer'
        }
        response = self.build_response(vnd_error, status_code=status.HTTP_404_NOT_FOUND)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_404(response, pointer='Not the correct pointer')
        assert f'Error `Not the correct pointer` not found in' in str(err.value)

    def test_status_pointer_requires_correct_error(self, vnd_error):
        vnd_error['errors'][0]['detail'] = 'Not found'
        vnd_error['errors'][0]['source'] = {
            'pointer': 'correct pointer'
        }
        response = self.build_response(vnd_error, status_code=status.HTTP_404_NOT_FOUND)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_404(response, error='Not the correct error', pointer='Not the correct pointer')
        assert f'Error `Not the correct error` not found in' in str(err.value)

    def test_status_in_second_error(self, vnd_error_404):
        vnd_error_404['errors'].append({'detail': 'another error'})
        response = self.build_response(vnd_error_404, status_code=status.HTTP_404_NOT_FOUND)

        AssertionHelper.HTTP_404(response, error='another error')

    def test_status_missing_in_multiple_errors(self, vnd_error_404):
        vnd_error_404['errors'].append({'detail': 'another error'})
        response = self.build_response(vnd_error_404, status_code=status.HTTP_404_NOT_FOUND)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_404(response, error='Not the correct error')
        assert f'Error `Not the correct error` not found in' in str(err.value)

    def test_exclusive_entity_refs_or_fields(self, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(), attributes={'test': 1})
        assert 'Use Only `entity_refs` or explicit `attributes`, `relationships`, `resource`, and `pk` but not both' \
               in str(err.value)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(), relationships={'test': 1})
        assert 'Use Only `entity_refs` or explicit `attributes`, `relationships`, `resource`, and `pk` but not both' \
               in str(err.value)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(), resource='test')
        assert 'Use Only `entity_refs` or explicit `attributes`, `relationships`, `resource`, and `pk` but not both' \
               in str(err.value)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(), pk='test')
        assert 'Use Only `entity_refs` or explicit `attributes`, `relationships`, `resource`, and `pk` but not both' \
               in str(err.value)

    def test_vnd_with_non_jsonapi_data(self):
        response = self.build_response(EXAMPLE_PLAIN)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, attributes=EXAMPLE_PLAIN)
        assert f'response does not contain `data` property' in str(err.value)

    def test_vnd_is_list(self, vnd_single, vnd_list):
        single_response = self.build_response(vnd_single)
        list_response = self.build_response(vnd_list)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(single_response, is_list=True)
        assert 'Response should be a list' in str(err.value)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(list_response)
        assert 'Response should not be a list' in str(err.value)

    def test_vnd_attributes_match(self, vnd_single):
        response = self.build_response(vnd_single)
        AssertionHelper.HTTP_200(response, attributes=EXAMPLE_RESOURCE['attributes'])

    def test_vnd_attributes_not_match(self, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, attributes=EXAMPLE_RESOURCE_2['attributes'])
        assert f'Attribute Value incorrect `{EXAMPLE_RESOURCE_2["attributes"]["name"]}` in ' in str(err.value)

    def test_vnd_relationships_should_be_entity_ref(self, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, relationships={'owner': EXAMPLE_RESOURCE_2})
        assert f'asserted relationship is not an EntityRef' in str(err.value)

    def test_vnd_relationships_match(self, vnd_single):
        response = self.build_response(vnd_single)

        AssertionHelper.HTTP_200(response, relationships={'owner': AssertionHelper.EntityRef(
            resource=EXAMPLE_USER['type'],
            pk=EXAMPLE_USER['id'],
        )})

    def test_vnd_relationships_match_list(self, vnd_single):
        response = self.build_response(vnd_single)

        AssertionHelper.HTTP_200(response, relationships={
            'owner': AssertionHelper.EntityRef(
                resource=EXAMPLE_USER['type'],
                pk=EXAMPLE_USER['id'],
            ),
            'children': [
                AssertionHelper.EntityRef(
                    resource=EXAMPLE_RESOURCE_2['type'],
                    pk=EXAMPLE_RESOURCE_2['id'],
                ),
                AssertionHelper.EntityRef(
                    resource=EXAMPLE_RESOURCE_4['type'],
                    pk=EXAMPLE_RESOURCE_4['id'],
                ),
            ]})

    def test_vnd_relationships_not_match(self, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, relationships={'owner': AssertionHelper.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                pk=EXAMPLE_RESOURCE['id'],
            )})
        assert f'EntityRef resource type `{EXAMPLE_RESOURCE["type"]}` does not match' in str(err.value)

    def test_vnd_relationships_not_match_in_list(self, vnd_single):
        response = self.build_response(vnd_single)

        relationship = AssertionHelper.EntityRef(resource=EXAMPLE_RESOURCE_3["type"],
                                                 pk=EXAMPLE_RESOURCE_3["id"],
                                                 attributes={})

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, relationships={'children': [
                AssertionHelper.EntityRef(
                    resource=EXAMPLE_RESOURCE_2['type'],
                    pk=EXAMPLE_RESOURCE_2['id'],
                ),
                relationship,
            ]})
        assert f'{relationship} NOT IN ' in str(err.value)

    def test_vnd_included_should_be_entity_ref(self, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, included=EXAMPLE_RESOURCE_2)
        assert f'asserted includes is not an EntityRef' in str(err.value)

    def test_vnd_included_full_match(self, vnd_single):
        response = self.build_response(vnd_single)

        AssertionHelper.HTTP_200(response, included=AssertionHelper.EntityRef(
            resource=EXAMPLE_RESOURCE_2['type'],
            pk=EXAMPLE_RESOURCE_2['id'],
            attributes=EXAMPLE_RESOURCE_2['attributes'],
        ))

    def test_vnd_included_full_not_match(self, vnd_single):
        response = self.build_response(vnd_single)
        include = AssertionHelper.EntityRef(
            resource=EXAMPLE_RESOURCE['type'],
            pk=EXAMPLE_RESOURCE['id'],
            attributes=EXAMPLE_RESOURCE['attributes'],
        )

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, included=include)
        assert f'{include} NOT IN' in str(err.value)

    def test_vnd_included_type_pk_match(self, vnd_single):
        response = self.build_response(vnd_single)

        AssertionHelper.HTTP_200(response, included=AssertionHelper.EntityRef(
            resource=EXAMPLE_RESOURCE_2['type'],
            pk=EXAMPLE_RESOURCE_2['id'],
        ))

    def test_vnd_included_type_pk_not_match(self, vnd_single):
        response = self.build_response(vnd_single)
        include = AssertionHelper.EntityRef(
            resource=EXAMPLE_RESOURCE['type'],
            pk=EXAMPLE_RESOURCE['id'],
        )

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, included=include)
        assert f'{include} NOT IN' in str(err.value)

    def test_vnd_included_attributes_match(self, vnd_single):
        response = self.build_response(vnd_single)

        AssertionHelper.HTTP_200(response, included=AssertionHelper.EntityRef(
            attributes=EXAMPLE_RESOURCE_2['attributes'],
        ))

    def test_vnd_included_attributes_not_match(self, vnd_single):
        response = self.build_response(vnd_single)
        include = AssertionHelper.EntityRef(
            attributes=EXAMPLE_RESOURCE['attributes'],
        )

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, included=include)
        assert f'{include} NOT IN' in str(err.value)

    def test_vnd_included_list_all_match(self, vnd_single):
        response = self.build_response(vnd_single)

        AssertionHelper.HTTP_200(response, included=[
            AssertionHelper.EntityRef(
                resource=EXAMPLE_RESOURCE_2['type'],
                pk=EXAMPLE_RESOURCE_2['id'],
                attributes=EXAMPLE_RESOURCE_2['attributes']),
            AssertionHelper.EntityRef(
                resource=EXAMPLE_USER['type'],
                pk=EXAMPLE_USER['id'],
                attributes=EXAMPLE_USER['attributes']),
        ])

    def test_vnd_included_list_one_match(self, vnd_single):
        response = self.build_response(vnd_single)
        include_1 = AssertionHelper.EntityRef(
            resource=EXAMPLE_RESOURCE['type'],
            pk=EXAMPLE_RESOURCE['id'],
            attributes=EXAMPLE_RESOURCE['attributes'])
        include_2 = AssertionHelper.EntityRef(
            resource=EXAMPLE_USER['type'],
            pk=EXAMPLE_USER['id'],
            attributes=EXAMPLE_USER['attributes'])

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, included=[include_1, include_2])
        assert f'{include_1} NOT IN' in str(err.value)

    def test_vnd_included_list_none_match(self, vnd_single):
        response = self.build_response(vnd_single)
        include_1 = AssertionHelper.EntityRef(
            resource=EXAMPLE_RESOURCE['type'],
            pk=EXAMPLE_RESOURCE['id'],
            attributes=EXAMPLE_RESOURCE['attributes'])
        include_2 = AssertionHelper.EntityRef(
            resource=EXAMPLE_RESOURCE_3['type'],
            pk=EXAMPLE_RESOURCE_3['id'],
            attributes=EXAMPLE_RESOURCE_3['attributes'])

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, included=[include_1, include_2])
        assert f'{include_1} NOT IN' in str(err.value)

    def test_entity_list_non_list_response(self, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=[AssertionHelper.EntityRef()])
        assert 'entity_refs should not be a list for a non-list response' in str(err.value)

    def test_vnd_entity_full_match(self, vnd_single):
        response = self.build_response(vnd_single)
        AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(
            resource=EXAMPLE_RESOURCE['type'],
            pk=EXAMPLE_RESOURCE['id'],
            attributes=EXAMPLE_RESOURCE['attributes'],
            relationships={'owner': AssertionHelper.EntityRef(
                resource=EXAMPLE_USER['type'],
                pk=EXAMPLE_USER['id'],
            )}
        ))

    def test_vnd_entity_full_type_not_match(self, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(
                resource=EXAMPLE_USER['type'],
                pk=EXAMPLE_RESOURCE['id'],
                attributes=EXAMPLE_RESOURCE['attributes'],
                relationships={'owner': AssertionHelper.EntityRef(
                    resource=EXAMPLE_USER['type'],
                    pk=EXAMPLE_USER['id'],
                )}
            ))
        assert f'Invalid Resource Type in' in str(err.value)

    def test_vnd_entity_full_id_not_match(self, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                pk=EXAMPLE_USER['id'],
                attributes=EXAMPLE_RESOURCE['attributes'],
                relationships={'owner': AssertionHelper.EntityRef(
                    resource=EXAMPLE_USER['type'],
                    pk=EXAMPLE_USER['id'],
                )}
            ))
        assert f'Invalid ID in' in str(err.value)

    def test_vnd_entity_full_attributes_missing(self, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                pk=EXAMPLE_RESOURCE['id'],
                attributes=EXAMPLE_USER['attributes'],
                relationships={'owner': AssertionHelper.EntityRef(
                    resource=EXAMPLE_USER['type'],
                    pk=EXAMPLE_USER['id'],
                )}
            ))
        assert f'Missing Attribute `username` in' in str(err.value)

    def test_vnd_entity_full_attributes_not_match(self, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                pk=EXAMPLE_RESOURCE['id'],
                attributes=EXAMPLE_RESOURCE_2['attributes'],
                relationships={'owner': AssertionHelper.EntityRef(
                    resource=EXAMPLE_USER['type'],
                    pk=EXAMPLE_USER['id'],
                )}
            ))
        assert f'Attribute Value incorrect `example 2` in' in str(err.value)

    def test_vnd_entity_full_relationships_type_not_match(self, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                pk=EXAMPLE_RESOURCE['id'],
                attributes=EXAMPLE_RESOURCE['attributes'],
                relationships={'owner': AssertionHelper.EntityRef(
                    resource=EXAMPLE_RESOURCE['type'],
                    pk=EXAMPLE_USER['id'],
                )}
            ))
        assert f'EntityRef resource type `{EXAMPLE_RESOURCE["type"]}` does not match' in str(err.value)

    def test_vnd_entity_full_relationships_pk_not_match(self, vnd_single):
        response = self.build_response(vnd_single)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                pk=EXAMPLE_RESOURCE['id'],
                attributes=EXAMPLE_RESOURCE['attributes'],
                relationships={'owner': AssertionHelper.EntityRef(
                    resource=EXAMPLE_USER['type'],
                    pk=EXAMPLE_RESOURCE['id'],
                )}
            ))
        assert f'EntityRef ID `{EXAMPLE_RESOURCE["id"]}` does not match' in str(err.value)

    def test_vnd_entity_type_pk_match(self, vnd_single):
        response = self.build_response(vnd_single)
        AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(
            resource=EXAMPLE_RESOURCE['type'],
            pk=EXAMPLE_RESOURCE['id'],
        ))

    def test_vnd_entity_type_pk_not_match(self, vnd_single):
        response = self.build_response(vnd_single)
        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(
                resource=EXAMPLE_USER['type'],
                pk=EXAMPLE_RESOURCE['id'],
            ))
        assert f'Invalid Resource Type in' in str(err.value)

    def test_vnd_entity_attribute_only_match(self, vnd_single):
        response = self.build_response(vnd_single)
        AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(
            attributes=EXAMPLE_RESOURCE['attributes']
        ))

    def test_vnd_entity_attribute_only_not_match(self, vnd_single):
        response = self.build_response(vnd_single)
        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(
                attributes=EXAMPLE_RESOURCE_2['attributes'],
            ))
        assert f'Attribute Value incorrect `example 2` in' in str(err.value)

    def test_vnd_list_entity_full_match(self, vnd_list):
        response = self.build_response(vnd_list)
        AssertionHelper.HTTP_200(response, is_list=True, entity_refs=AssertionHelper.EntityRef(
            resource=EXAMPLE_RESOURCE['type'],
            pk=EXAMPLE_RESOURCE['id'],
            attributes=EXAMPLE_RESOURCE['attributes'],
            relationships={'owner': AssertionHelper.EntityRef(
                resource=EXAMPLE_USER['type'],
                pk=EXAMPLE_USER['id'],
            )}
        ))

    def test_vnd_list_entity_list_all_match(self, vnd_list, entity_ref_1, entity_ref_3):
        response = self.build_response(vnd_list)
        AssertionHelper.HTTP_200(response, is_list=True, entity_refs=[entity_ref_1, entity_ref_3])

    def test_vnd_list_count(self, vnd_list):
        response = self.build_response(vnd_list)
        AssertionHelper.HTTP_200(response, is_list=True, count=len(vnd_list['data']))

    def test_vnd_list_wrong_count(self, vnd_list):
        list_length = len(vnd_list['data'])
        response = self.build_response(vnd_list)
        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, is_list=True, count=list_length - 1)
        assert f'Difference in count of response_data, got {list_length} expected {list_length - 1}' in str(err.value)

    def test_vnd_single_count(self, vnd_single):
        response = self.build_response(vnd_single)
        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, count=1)
        assert f'Count is only checked when response is list' in str(err.value)

    def test_vnd_list_ordering(self, vnd_list, entity_ref_1, entity_ref_3):
        response = self.build_response(vnd_list)
        AssertionHelper.HTTP_200(response, is_list=True, entity_refs=[entity_ref_1, entity_ref_3], check_ordering=True)

    def test_vnd_list_wrong_ordering(self, vnd_list, entity_ref_1, entity_ref_3):
        response = self.build_response(vnd_list)
        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, is_list=True, entity_refs=[entity_ref_3, entity_ref_1],
                                     check_ordering=True)
        assert 'Invalid ID in ' in str(err.value)

    def test_vnd_list_wrong_ordering_amount(self, vnd_list, entity_ref_1, entity_ref_3):
        response = self.build_response(vnd_list)
        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, is_list=True, entity_refs=[entity_ref_1, entity_ref_3, entity_ref_1],
                                     check_ordering=True)
        assert 'Error: more entity refs supplied than available in response data. ' in str(err.value)

    def test_vnd_single_ordering(self, vnd_single, entity_ref_1):
        response = self.build_response(vnd_single)
        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=entity_ref_1, check_ordering=True)
        assert f'Ordering is only checked when response is list' in str(err.value)

    def test_vnd_list_entity_list_one_not_match(self, vnd_list, entity_ref_1, entity_ref_3):
        response = self.build_response(vnd_list)
        entity_ref_3.pk = EXAMPLE_RESOURCE_2['id']

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, is_list=True, entity_refs=[entity_ref_1, entity_ref_3])
        assert f'{entity_ref_3} NOT IN' in str(err.value)

    def test_plain_json_valid_parameters(self):
        response = self.build_response(EXAMPLE_PLAIN)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, vnd=False, entity_refs={AssertionHelper.EntityRef()})
        assert f'entity_refs not valid when vnd=False' in str(err.value)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, vnd=False, relationships=AssertionHelper.EntityRef())
        assert f'relationships not valid when vnd=False' in str(err.value)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, vnd=False, included=AssertionHelper.EntityRef())
        assert f'included not valid when vnd=False' in str(err.value)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, vnd=False)
        assert f'attributes must be provided when vnd=False' in str(err.value)

    def test_plain_json_attributes(self):
        response = self.build_response(EXAMPLE_PLAIN)

        AssertionHelper.HTTP_200(response, vnd=False, attributes=EXAMPLE_PLAIN)

    def test_plain_json_attributes_top_level_missing(self):
        response = self.build_response(EXAMPLE_PLAIN)

        invalid_attributes = EXAMPLE_PLAIN.copy()
        invalid_attributes['new_field'] = 1

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, vnd=False, attributes=invalid_attributes)
        assert f'Missing Attribute `new_field` in ' in str(err.value)

    def test_plain_json_attributes_top_level_mismatch(self):
        response = self.build_response(EXAMPLE_PLAIN)

        invalid_attributes = EXAMPLE_PLAIN.copy()
        invalid_attributes['id'] = 1

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, vnd=False, attributes=invalid_attributes)
        assert f'Attribute Value incorrect `1` in ' in str(err.value)

    def test_plain_json_attributes_nested_missing(self):
        response = self.build_response(EXAMPLE_PLAIN)

        invalid_attributes = EXAMPLE_PLAIN.copy()
        invalid_attributes['owner'] = EXAMPLE_PLAIN['owner'].copy()
        invalid_attributes['owner']['new_field'] = 'test'

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, vnd=False, attributes=invalid_attributes)
        assert f'Missing Attribute `new_field` in ' in str(err.value)

    def test_plain_json_attributes_nested_mismatch(self):
        response = self.build_response(EXAMPLE_PLAIN)

        invalid_attributes = EXAMPLE_PLAIN.copy()
        invalid_attributes['owner'] = EXAMPLE_PLAIN['owner'].copy()
        invalid_attributes['owner']['id'] = 'test'

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, vnd=False, attributes=invalid_attributes)
        assert f'Missing Attribute `id` in ' in str(err.value)

    def test_plain_json_attributes_list_assertions(self):
        single_response = self.build_response(EXAMPLE_PLAIN)
        list_response = self.build_response([EXAMPLE_PLAIN, EXAMPLE_PLAIN_2])

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(single_response, vnd=False, is_list=True, attributes=EXAMPLE_PLAIN)
        assert f'Response should be a list' in str(err.value)

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(list_response, vnd=False, attributes=EXAMPLE_PLAIN)
        assert f'Response should not be a list' in str(err.value)

    def test_plain_json_attributes_list_single_match(self):
        response = self.build_response([EXAMPLE_PLAIN, EXAMPLE_PLAIN_2])

        AssertionHelper.HTTP_200(response, vnd=False, is_list=True, attributes=EXAMPLE_PLAIN)

    def test_plain_json_attributes_list_both_match(self):
        response = self.build_response([EXAMPLE_PLAIN, EXAMPLE_PLAIN_2])

        AssertionHelper.HTTP_200(response, vnd=False, is_list=True, attributes=[EXAMPLE_PLAIN, EXAMPLE_PLAIN_2])

    def test_plain_json_attributes_list_one_missing(self):
        response = self.build_response([EXAMPLE_PLAIN, EXAMPLE_PLAIN_2])

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, vnd=False, is_list=True, attributes=[EXAMPLE_PLAIN, EXAMPLE_PLAIN_3])
        assert f'{EXAMPLE_PLAIN_3} NOT IN ' in str(err.value)

    def test_plain_json_attributes_list_ordering(self):
        response = self.build_response([EXAMPLE_PLAIN, EXAMPLE_PLAIN_2])

        AssertionHelper.HTTP_200(response, vnd=False, is_list=True, attributes=[EXAMPLE_PLAIN, EXAMPLE_PLAIN_2],
                                 check_ordering=True)

    def test_plain_json_attributes_list_wrong_ordering(self):
        response = self.build_response([EXAMPLE_PLAIN, EXAMPLE_PLAIN_2])

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, vnd=False, is_list=True, attributes=[EXAMPLE_PLAIN_2, EXAMPLE_PLAIN],
                                     check_ordering=True)
        assert f'Attribute Value incorrect ' in str(err.value)

    def test_plain_json_attributes_list_wrong_ordering_size(self):
        response = self.build_response([EXAMPLE_PLAIN, EXAMPLE_PLAIN_2])

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, vnd=False, is_list=True, check_ordering=True,
                                     attributes=[EXAMPLE_PLAIN, EXAMPLE_PLAIN_2, EXAMPLE_PLAIN])
        assert 'Error: more attributes supplied than available in response. 3 found asserted 2' in str(err.value)

    def test_plain_json_attributes_list_nested_missing(self):
        response = self.build_response([EXAMPLE_PLAIN, EXAMPLE_PLAIN_2])

        invalid_attributes = EXAMPLE_PLAIN.copy()
        invalid_attributes['owner'] = EXAMPLE_PLAIN['owner'].copy()
        invalid_attributes['owner']['new_field'] = 'test'

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, vnd=False, is_list=True, attributes=invalid_attributes)
        assert f'{invalid_attributes} NOT IN ' in str(err.value)

    def test_plain_json_attributes_list_nested_mismatch(self):
        response = self.build_response([EXAMPLE_PLAIN, EXAMPLE_PLAIN_2])

        invalid_attributes = EXAMPLE_PLAIN.copy()
        invalid_attributes['owner'] = EXAMPLE_PLAIN['owner'].copy()
        invalid_attributes['owner']['id'] = 'test'

        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, vnd=False, is_list=True, attributes=invalid_attributes)
        assert f'{invalid_attributes} NOT IN ' in str(err.value)

    def test_plain_json_list_count(self):
        response = self.build_response([EXAMPLE_PLAIN, EXAMPLE_PLAIN_2])
        AssertionHelper.HTTP_200(response, vnd=False, is_list=True, count=2,
                                 attributes=[EXAMPLE_PLAIN, EXAMPLE_PLAIN_2])

    def test_plain_json_list_wrong_count(self):
        response = self.build_response([EXAMPLE_PLAIN, EXAMPLE_PLAIN_2])
        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, vnd=False, attributes=[EXAMPLE_PLAIN, EXAMPLE_PLAIN_2], is_list=True,
                                     count=1)
        assert 'Difference in count of response_data, got 2 expected 1' in str(err.value)

    def test_plain_json_single_count(self, vnd_single):
        response = self.build_response(vnd_single)
        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, count=1)
        assert f'Count is only checked when response is list' in str(err.value)

    def test_vnd_meta(self, vnd_single):
        response = self.build_response(vnd_single)
        AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(
            resource=EXAMPLE_RESOURCE['type'],
            meta={
                'key': 'value',
                'other_key': 'other_value'
            },
         ))

    def test_vnd_meta_mismatch(self, vnd_single):
        response = self.build_response(vnd_single)
        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                meta={
                    'key': 'different value'
                },
             ))
        assert f'Meta field `key` had value `value` not `different value` as expected.' in str(err.value)

    def test_vnd_meta_invalid_key(self, vnd_single):
        response = self.build_response(vnd_single)
        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                meta={
                    'invalid_key': 'value'
                },
             ))
        assert f'Meta field `invalid_key` not found' in str(err.value)

    def test_vnd_no_meta(self, vnd_single):
        vnd_single['data'].pop('meta')
        response = self.build_response(vnd_single)
        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                meta={
                    'key': 'value'
                },
             ))
        assert 'Meta missing' in str(err.value)

    def test_vnd_invalid_meta_format(self, vnd_single):
        response = self.build_response(vnd_single)
        with pytest.raises(AssertionError) as err:
            AssertionHelper.HTTP_200(response, entity_refs=AssertionHelper.EntityRef(
                resource=EXAMPLE_RESOURCE['type'],
                meta=[{
                    'key': 'value'
                }],
             ))
        assert 'Invalid format for meta data <class \'list\'>, must be dict' in str(err.value)

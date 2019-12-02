import json

import django
# We run django.setup() in order to auto populate the base django's app models for testing purposes
import pytest
from rest_framework import status
from rest_framework.response import Response
from rest_framework_json_api import serializers

from tests.django_mocking.models import BasicModel

try:
    django.setup()
except Exception as exc:
    raise exc

from shipchain_common.viewsets import ActionConfiguration, ConfigurableGenericViewSet
from shipchain_common.renderers import CGVSJsonRenderer


class DefaultSerializer(serializers.ModelSerializer):

    class Meta:
        model = BasicModel
        fields = '__all__'

    class JSONAPIMeta:
        resource_name = 'DefaultSerializer'


class ListResponseSerializer(DefaultSerializer):
    class JSONAPIMeta:
        resource_name = 'ListResponseSerializer'


class CreateRequestSerializer(DefaultSerializer):
    class JSONAPIMeta:
        resource_name = 'CreateRequestSerializer'


class CreateResponseSerializer(DefaultSerializer):
    class JSONAPIMeta:
        resource_name = 'CreateResponseSerializer'


class CustomActionSerializer(DefaultSerializer):
    class JSONAPIMeta:
        resource_name = 'CustomActionSerializer'


class CustomActionCSVSerializer(DefaultSerializer):
    class JSONAPIMeta:
        resource_name = 'CustomActionCSVSerializer'


class TestCGVSJsonRenderer:

    @pytest.fixture
    def viewset(self):
        class TestViewSet(ConfigurableGenericViewSet):
            kwargs = {}
            request = {}
            response = Response(status=status.HTTP_200_OK)
            format_kwarg = ''
            serializer_class = DefaultSerializer

        return TestViewSet()

    def test_get_resource_from_configurable_serializer(self, viewset):
        viewset.configuration = {
            'list': ActionConfiguration(
                response_serializer=ListResponseSerializer,
            ),
            'create': ActionConfiguration(
                request_serializer=CreateRequestSerializer,
                response_serializer=CreateResponseSerializer,
            ),
            'custom_action': ActionConfiguration(
                request_serializer=CustomActionSerializer,
                response_serializer={
                    'default': CustomActionSerializer,
                    'csv': CustomActionCSVSerializer,
                },
            ),
        }

        renderer = CGVSJsonRenderer()
        response_data = DefaultSerializer(BasicModel(my_field='1')).data
        renderer_context = {'view': viewset, 'request': viewset.request, 'response': viewset.response}

        viewset.action = 'update'
        response = renderer.render(response_data, renderer_context=renderer_context)
        response = json.loads(response)
        assert response['data']['type'] == 'DefaultSerializer'

        viewset.action = 'list'
        response = renderer.render(response_data, renderer_context=renderer_context)
        response = json.loads(response)
        assert response['data']['type'] == 'ListResponseSerializer'

        viewset.action = 'create'
        response = renderer.render(response_data, renderer_context=renderer_context)
        response = json.loads(response)
        assert response['data']['type'] == 'CreateResponseSerializer'

        viewset.action = 'custom_action'
        response = renderer.render(response_data, renderer_context=renderer_context)
        response = json.loads(response)
        assert response['data']['type'] == 'CustomActionSerializer'

        viewset.action = 'custom_action'
        viewset.kwargs['format'] = 'csv'
        response = renderer.render(response_data, renderer_context=renderer_context)
        response = json.loads(response)
        assert response['data']['type'] == 'CustomActionCSVSerializer'
        viewset.kwargs['format'] = None

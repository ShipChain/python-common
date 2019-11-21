import django
# We run django.setup() in order to auto populate the base django's app models for testing purposes
import pytest
from rest_framework import status

try:
    django.setup()
except Exception as exc:
    raise exc

from shipchain_common.mixins import SerializationType, MultiSerializerViewSetMixin, MultiPermissionViewSetMixin
from shipchain_common.viewsets import ActionConfiguration, ConfigurableGenericViewSet


class FakePermission:
    name = 'fake1'

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name


class FakePermission2(FakePermission):
    name = 'fake2'


class FakePermission3(FakePermission):
    name = 'fake3'


class DefaultSerializer:
    pass


class ListResponseSerializer:
    pass


class CreateRequestSerializer:
    pass


class CreateResponseSerializer:
    pass


class CustomActionSerializer:
    pass


class CustomActionCSVSerializer:
    pass


class TestConfigurableGenericViewSet:

    def test_restricted_serializer_mixin(self):
        class TestViewSet(MultiSerializerViewSetMixin, ConfigurableGenericViewSet):
            kwargs = {}
            serializer_class = DefaultSerializer
            permission_classes = [FakePermission2]
    
        with pytest.raises(AttributeError) as attr_err:
            TestViewSet()
        assert 'Cannot use MultiSerializerViewSetMixin when using ConfigurableGenericViewSet' in str(attr_err.value)
    
    def test_restricted_permission_mixin(self):
        class TestViewSet(MultiPermissionViewSetMixin, ConfigurableGenericViewSet):
            kwargs = {}
            serializer_class = DefaultSerializer
            permission_classes = [FakePermission2]
    
        with pytest.raises(AttributeError) as attr_err:
            TestViewSet()
        assert 'Cannot use MultiPermissionViewSetMixin when using ConfigurableGenericViewSet' in str(attr_err.value)
    
    def test_needs_configuration(self):
        class TestViewSet(ConfigurableGenericViewSet):
            kwargs = {}
            serializer_class = DefaultSerializer
            permission_classes = [FakePermission2]
        viewset = TestViewSet()
    
        with pytest.raises(AssertionError) as ass_err:
            viewset.get_configuration()
        assert '\'TestViewSet\' should include a `configuration` attribute.' in str(ass_err.value)

    def test_config_validation_list(self):
        class TestViewSet(ConfigurableGenericViewSet):
            kwargs = {}
            serializer_class = DefaultSerializer
            permission_classes = [FakePermission2]
            configuration = {
                'list': ActionConfiguration(request_serializer=ListResponseSerializer)
            }
        viewset = TestViewSet()
    
        with pytest.raises(AttributeError) as attr_err:
            viewset.get_configuration()
        assert 'request_serializer not valid for action list' in str(attr_err.value)

        viewset.configuration['list'] = ActionConfiguration(request_validation=True)

        with pytest.raises(AttributeError) as attr_err:
            viewset.get_configuration()
        assert 'request_validation not valid for action list' in str(attr_err.value)

        viewset.configuration['list'] = ActionConfiguration(success_status=200)

        with pytest.raises(AttributeError) as attr_err:
            viewset.get_configuration()
        assert 'success_status not valid for action list' in str(attr_err.value)

    def test_configurable_generic_view_set(self):
        class TestViewSet(ConfigurableGenericViewSet):
            kwargs = {}
            serializer_class = DefaultSerializer
            permission_classes = [FakePermission2]
    
            configuration = {
                'list': ActionConfiguration(
                    response_serializer=ListResponseSerializer,
                    permission_classes=[FakePermission, FakePermission2],
                    required_user_permissions=['feature.permission', 'feature.permission2'],
                ),
                'create': ActionConfiguration(
                    request_serializer=CreateRequestSerializer,
                    request_validation=False,
                    response_serializer=CreateResponseSerializer,
                    permission_classes=[FakePermission],
                    required_user_permissions=['feature.permission'],
                    success_status=status.HTTP_202_ACCEPTED,
                ),
                'custom_action': ActionConfiguration(
                    request_serializer=CustomActionSerializer,
                    response_serializer={
                        'default': CustomActionSerializer,
                        'csv': CustomActionCSVSerializer,
                    },
                    permission_classes=[FakePermission, FakePermission3],
                    required_user_permissions='feature.custom_permission',
                ),
            }
    
        viewset = TestViewSet()
    
        viewset.action = 'list'
        assert viewset.get_serializer_class() == DefaultSerializer
        assert viewset.get_serializer_class(SerializationType.RESPONSE) == ListResponseSerializer
        assert viewset.get_permissions() == [FakePermission, FakePermission2]
        assert viewset.configuration['list'].serializer is None
        assert viewset.action_user_permissions['list'] == ['feature.permission', 'feature.permission2']
    
        viewset.action = 'create'
        assert viewset.get_serializer_class() == CreateRequestSerializer
        assert viewset.get_serializer_class(SerializationType.RESPONSE) == CreateResponseSerializer
        assert viewset.get_permissions() == [FakePermission]
        assert viewset.configuration['create'].raise_validation is False
        assert viewset.configuration['create'].serializer is None
        assert viewset.action_user_permissions['create'] == ['feature.permission']
    
        viewset.action = 'custom_action'
        assert viewset.get_serializer_class() == CustomActionSerializer
        assert viewset.get_serializer_class(SerializationType.RESPONSE) == CustomActionSerializer
        assert viewset.get_permissions() == [FakePermission, FakePermission3]
        assert viewset.configuration['custom_action'].serializer is None
        assert viewset.action_user_permissions['custom_action'] == ['feature.custom_permission']
        viewset.kwargs['format'] = 'csv'
        assert viewset.get_serializer_class(SerializationType.RESPONSE) == CustomActionCSVSerializer
        viewset.kwargs['format'] = 'invalid'
        assert viewset.get_serializer_class(SerializationType.RESPONSE) == CustomActionSerializer
    
        viewset.action = 'update'
        assert viewset.get_serializer_class() == DefaultSerializer
        assert viewset.get_permissions() == [FakePermission2]
        assert 'update' not in viewset.configuration
        assert 'update' not in viewset.action_user_permissions

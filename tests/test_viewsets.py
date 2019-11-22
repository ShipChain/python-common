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
    def __init__(self, *args, **kwargs):
        pass


class ListResponseSerializer(DefaultSerializer):
    pass


class CreateRequestSerializer(DefaultSerializer):
    pass


class CreateResponseSerializer(DefaultSerializer):
    pass


class CustomActionSerializer(DefaultSerializer):
    pass


class CustomActionCSVSerializer(DefaultSerializer):
    pass


class TestActionConfiguration:

    def test_validation_list(self):
        action = 'list'
        config = ActionConfiguration(request_serializer=ListResponseSerializer)

        with pytest.raises(AttributeError) as attr_err:
            config.validate_action(action)
        assert 'request_serializer not valid for action list' in str(attr_err.value)

        config = ActionConfiguration(request_validation=True)

        with pytest.raises(AttributeError) as attr_err:
            config.validate_action(action)
        assert 'request_validation not valid for action list' in str(attr_err.value)

        config = ActionConfiguration(success_status=200)

        with pytest.raises(AttributeError) as attr_err:
            config.validate_action(action)
        assert 'success_status not valid for action list' in str(attr_err.value)

    def test_validation_retrieve(self):
        action = 'retrieve'
        config = ActionConfiguration(request_serializer=ListResponseSerializer)

        with pytest.raises(AttributeError) as attr_err:
            config.validate_action(action)
        assert 'request_serializer not valid for action retrieve' in str(attr_err.value)

        config = ActionConfiguration(request_validation=True)

        with pytest.raises(AttributeError) as attr_err:
            config.validate_action(action)
        assert 'request_validation not valid for action retrieve' in str(attr_err.value)

        config = ActionConfiguration(success_status=200)

        with pytest.raises(AttributeError) as attr_err:
            config.validate_action(action)
        assert 'success_status not valid for action retrieve' in str(attr_err.value)

    def test_validation_destroy(self):
        action = 'destroy'
        config = ActionConfiguration(request_serializer=ListResponseSerializer)

        with pytest.raises(AttributeError) as attr_err:
            config.validate_action(action)
        assert 'request_serializer not valid for action destroy' in str(attr_err.value)

        config = ActionConfiguration(request_validation=True)

        with pytest.raises(AttributeError) as attr_err:
            config.validate_action(action)
        assert 'request_validation not valid for action destroy' in str(attr_err.value)

        config = ActionConfiguration(success_status=200)

        with pytest.raises(AttributeError) as attr_err:
            config.validate_action(action)
        assert 'success_status not valid for action destroy' in str(attr_err.value)

        config = ActionConfiguration(serializer=ListResponseSerializer)

        with pytest.raises(AttributeError) as attr_err:
            config.validate_action(action)
        assert 'serializers are not valid for action destroy' in str(attr_err.value)

        config = ActionConfiguration(response_serializer=ListResponseSerializer)

        with pytest.raises(AttributeError) as attr_err:
            config.validate_action(action)
        assert 'serializers are not valid for action destroy' in str(attr_err.value)

    def test_standardize_serializer(self):
        """
        Providing just a serializer should populate both the Request and Response.default references
        Re-running standardize_serializer_properties should not change the standardized properties
        """
        config = ActionConfiguration(serializer=DefaultSerializer)

        assert config.serializer == DefaultSerializer
        assert config.request_serializer is None
        assert config.response_serializer is None
        assert config.re_serialize_response is False

        config.standardize_serializer_properties()

        assert config.serializer is None
        assert config.request_serializer == DefaultSerializer
        assert isinstance(config.response_serializer, ActionConfiguration.ResponseSerializers)
        assert config.response_serializer.default == DefaultSerializer
        assert config.re_serialize_response is False

        config.standardize_serializer_properties()

        assert config.serializer is None
        assert config.request_serializer == DefaultSerializer
        assert isinstance(config.response_serializer, ActionConfiguration.ResponseSerializers)
        assert config.response_serializer.default == DefaultSerializer
        assert config.re_serialize_response is False

    def test_standardize_request_serializer(self):
        """
        Providing just a request_serializer should populate only the Request reference.
        Since we don't have a response_serializer set, the get_serializer in the ConfigurableGenericViewSet
        will return the class level `serializer_class` and we don't know if it's different than our
        request_serializer, so we will set `re_serializer_response` to True.
        Re-running standardize_serializer_properties should not change the standardized properties
        """
        config = ActionConfiguration(request_serializer=DefaultSerializer)

        assert config.serializer is None
        assert config.request_serializer == DefaultSerializer
        assert config.response_serializer is None
        assert config.re_serialize_response is False

        config.standardize_serializer_properties()

        assert config.serializer is None
        assert config.request_serializer == DefaultSerializer
        assert config.response_serializer is None
        assert config.re_serialize_response is True

        config.standardize_serializer_properties()

        assert config.serializer is None
        assert config.request_serializer == DefaultSerializer
        assert config.response_serializer is None
        assert config.re_serialize_response is True

    def test_standardize_response_serializer(self):
        """
        Providing just a response_serializer should populate only the Response.default reference.
        Since we don't have a request_serializer set, the get_serializer in the ConfigurableGenericViewSet
        will return the class level `serializer_class` and we don't know if it's different than our
        response_serializer, so we will set `re_serializer_response` to True.
        Re-running standardize_serializer_properties should not change the standardized properties
        """
        config = ActionConfiguration(response_serializer=DefaultSerializer)

        assert config.serializer is None
        assert config.request_serializer is None
        assert config.response_serializer == DefaultSerializer
        assert config.re_serialize_response is False

        config.standardize_serializer_properties()

        assert config.serializer is None
        assert config.request_serializer is None
        assert isinstance(config.response_serializer, ActionConfiguration.ResponseSerializers)
        assert config.response_serializer.default == DefaultSerializer
        assert config.re_serialize_response is True

        config.standardize_serializer_properties()

        assert config.serializer is None
        assert config.request_serializer is None
        assert isinstance(config.response_serializer, ActionConfiguration.ResponseSerializers)
        assert config.response_serializer.default == DefaultSerializer
        assert config.re_serialize_response is True

    def test_standardize_both_serializer(self):
        """
        Providing both should populate both the Request and the Response.default reference.
        Since we are setting both request and response, so we will set `re_serializer_response` to True.
        Re-running standardize_serializer_properties should not change the standardized properties
        """
        config = ActionConfiguration(
            request_serializer=CreateRequestSerializer,
            response_serializer=CreateResponseSerializer,
        )

        assert config.serializer is None
        assert config.request_serializer == CreateRequestSerializer
        assert config.response_serializer == CreateResponseSerializer
        assert config.re_serialize_response is False

        config.standardize_serializer_properties()

        assert config.serializer is None
        assert config.request_serializer == CreateRequestSerializer
        assert isinstance(config.response_serializer, ActionConfiguration.ResponseSerializers)
        assert config.response_serializer.default == CreateResponseSerializer
        assert config.re_serialize_response is True

        config.standardize_serializer_properties()

        assert config.serializer is None
        assert config.request_serializer == CreateRequestSerializer
        assert isinstance(config.response_serializer, ActionConfiguration.ResponseSerializers)
        assert config.response_serializer.default == CreateResponseSerializer
        assert config.re_serialize_response is True

    def test_standardize_response_dict(self):
        """
        Providing response_serializer as a dict should populate the ResponseSerializers instance correctly
        """
        config = ActionConfiguration(
            response_serializer={
                'default': CustomActionSerializer,
            }
        )

        assert isinstance(config.response_serializer, dict)
        assert 'default' in config.response_serializer
        assert config.response_serializer['default'] == CustomActionSerializer

        config.standardize_serializer_properties()

        assert isinstance(config.response_serializer, ActionConfiguration.ResponseSerializers)
        assert config.response_serializer.default == CustomActionSerializer

    def test_standardize_response_dict_no_default(self):
        """
        Providing response_serializer as a dict without a default should raise an AttributeError
        """
        config = ActionConfiguration(
            response_serializer={
                'other': CustomActionSerializer,
            }
        )

        assert isinstance(config.response_serializer, dict)
        assert 'other' in config.response_serializer
        assert config.response_serializer['other'] == CustomActionSerializer

        with pytest.raises(AssertionError) as ass_err:
            config.standardize_serializer_properties()
        assert 'response_serializer needs a default provided' in str(ass_err.value)

    def test_standardize_response_dict_many(self):
        """
        Providing response_serializer as a dict with multiple properties
        should populate the ResponseSerializers instance correctly
        """
        config = ActionConfiguration(
            response_serializer={
                'default': CustomActionSerializer,
                'csv': CustomActionCSVSerializer,
            }
        )

        assert isinstance(config.response_serializer, dict)
        assert 'default' in config.response_serializer
        assert 'csv' in config.response_serializer
        assert config.response_serializer['default'] == CustomActionSerializer
        assert config.response_serializer['csv'] == CustomActionCSVSerializer

        config.standardize_serializer_properties()

        assert isinstance(config.response_serializer, ActionConfiguration.ResponseSerializers)
        assert config.response_serializer.default == CustomActionSerializer
        assert config.response_serializer.csv == CustomActionCSVSerializer

    def test_standardize_response_class(self):
        """
        Providing response_serializer as a dict should populate the ResponseSerializers instance correctly
        """
        config = ActionConfiguration(
            response_serializer=ActionConfiguration.ResponseSerializers(
                default=CustomActionSerializer,
            )
        )

        assert isinstance(config.response_serializer, ActionConfiguration.ResponseSerializers)
        assert config.response_serializer.default == CustomActionSerializer

        config.standardize_serializer_properties()

        assert isinstance(config.response_serializer, ActionConfiguration.ResponseSerializers)
        assert config.response_serializer.default == CustomActionSerializer

    def test_standardize_response_class_no_default(self):
        """
        Providing response_serializer as a dict without a default should raise an AttributeError
        """

        with pytest.raises(AssertionError) as ass_err:
            ActionConfiguration(
                response_serializer=ActionConfiguration.ResponseSerializers(
                    other=CustomActionSerializer,
                )
            )
        assert 'response_serializer needs a default provided' in str(ass_err.value)

    def test_standardize_response_class_many(self):
        """
        Providing response_serializer as a dict with multiple properties
        should populate the ResponseSerializers instance correctly
        """
        config = ActionConfiguration(
            response_serializer=ActionConfiguration.ResponseSerializers(
                default=CustomActionSerializer,
                csv=CustomActionCSVSerializer,
            )
        )

        assert isinstance(config.response_serializer, ActionConfiguration.ResponseSerializers)
        assert config.response_serializer.default == CustomActionSerializer
        assert config.response_serializer.csv == CustomActionCSVSerializer

        config.standardize_serializer_properties()

        assert isinstance(config.response_serializer, ActionConfiguration.ResponseSerializers)
        assert config.response_serializer.default == CustomActionSerializer
        assert config.response_serializer.csv == CustomActionCSVSerializer


class TestConfigurableGenericViewSet:

    @pytest.fixture
    def viewset(self):
        class TestViewSet(ConfigurableGenericViewSet):
            kwargs = {}
            request = {}
            format_kwarg = ''
            serializer_class = DefaultSerializer
            permission_classes = [FakePermission2]
        return TestViewSet()

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
    
    def test_needs_configuration(self, viewset):
        with pytest.raises(AssertionError) as ass_err:
            viewset.get_configuration()
        assert '\'TestViewSet\' should include a `configuration` attribute.' in str(ass_err.value)

    def test_configurable_generic_view_set(self, viewset):
        viewset.configuration = {
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
    
        viewset.action = 'list'
        assert viewset.get_serializer().__class__ == DefaultSerializer
        assert viewset.get_serializer(serialization_type=SerializationType.RESPONSE).__class__ == ListResponseSerializer
        assert viewset.get_serializer_class() == DefaultSerializer
        assert viewset.get_serializer_class(SerializationType.RESPONSE) == ListResponseSerializer
        assert viewset.get_permissions() == [FakePermission, FakePermission2]
        assert viewset.configuration['list'].serializer is None
        assert viewset.action_user_permissions['list'] == ['feature.permission', 'feature.permission2']
    
        viewset.action = 'create'
        assert viewset.get_serializer().__class__ == CreateRequestSerializer
        assert viewset.get_serializer(serialization_type=SerializationType.RESPONSE).__class__ == CreateResponseSerializer
        assert viewset.get_serializer_class() == CreateRequestSerializer
        assert viewset.get_serializer_class(SerializationType.RESPONSE) == CreateResponseSerializer
        assert viewset.get_permissions() == [FakePermission]
        assert viewset.configuration['create'].raise_validation is False
        assert viewset.configuration['create'].serializer is None
        assert viewset.action_user_permissions['create'] == ['feature.permission']
    
        viewset.action = 'custom_action'
        assert viewset.get_serializer().__class__ == CustomActionSerializer
        assert viewset.get_serializer(serialization_type=SerializationType.RESPONSE).__class__ == CustomActionSerializer
        assert viewset.get_serializer_class() == CustomActionSerializer
        assert viewset.get_serializer_class(SerializationType.RESPONSE) == CustomActionSerializer
        assert viewset.get_permissions() == [FakePermission, FakePermission3]
        assert viewset.configuration['custom_action'].serializer is None
        assert viewset.action_user_permissions['custom_action'] == ['feature.custom_permission']
        viewset.kwargs['format'] = 'csv'
        assert viewset.get_serializer_class(SerializationType.RESPONSE) == CustomActionCSVSerializer
        viewset.kwargs['format'] = 'invalid'
        assert viewset.get_serializer_class(SerializationType.RESPONSE) == CustomActionSerializer
        viewset.kwargs['format'] = None
    
        viewset.action = 'update'
        assert viewset.get_serializer().__class__ == DefaultSerializer
        assert viewset.get_serializer(serialization_type=SerializationType.RESPONSE).__class__ == DefaultSerializer
        assert viewset.get_serializer_class() == DefaultSerializer
        assert viewset.get_serializer_class(SerializationType.RESPONSE) == DefaultSerializer
        assert viewset.get_permissions() == [FakePermission2]
        assert 'update' not in viewset.configuration
        assert 'update' not in viewset.action_user_permissions

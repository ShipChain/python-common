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
from rest_framework.viewsets import GenericViewSet
from rest_framework.settings import api_settings

from . import mixins

FORMAT_SUFFIX = api_settings.FORMAT_SUFFIX_KWARG


class ActionConfiguration:
    """
    Class to hold the configuration settings for a specific Action within a ViewSet.
    All values are optional and default to None if not provided.  Validations run against the
    default actions (CRUDL) to ensure no invalid or conflicting settings are provided.
    """

    class ResponseSerializers:
        """
        Response can be serialized multiple ways depending on FORMAT_SUFFIX_KWARG.
        This class holds references to the serializers used for each case.
        """
        def __init__(self, **kwargs):
            self.default = None
            self.__dict__.update(**kwargs)
            if self.default is None:
                raise AttributeError(f'response_serializer needs a default provided')

    # pylint: disable=too-many-arguments
    def __init__(self,
                 serializer=None,
                 request_serializer=None,
                 response_serializer=None,
                 request_validation=None,
                 permission_classes=None,
                 required_user_permissions=None,
                 success_status=None):

        self.__action_validation_completed = False
        self.__serializer_standardization_completed = False

        self.serializer = serializer
        self.request_serializer = request_serializer
        self.response_serializer = response_serializer
        self.request_validation = request_validation
        self.permission_classes = permission_classes
        self.required_user_permissions = required_user_permissions
        self.success_status = success_status

        self.re_serialize_response = False

        self._validate_configuration()

    def _validate_configuration(self):
        """
        Validate that the combination of provided configuration options are valid.

        `serializer` can be provided as a the serializer class for both the incoming and outgoing data.
        Or the specific `request_serializer` and `response_serializer` can be set.  But if `serializer`
        is set, there should not be a setting for `request_serializer` or `response_serializer`.

        Ensures request_validation is a proper boolean.

        :raises AttributeError:
        """

        if self.serializer and (self.request_serializer or self.response_serializer):
            raise AttributeError('serializer cannot be provided if either '
                                 'request_serializer or response_serializer are provided')

        if self.request_validation is not None and not isinstance(self.request_validation, bool):
            raise AttributeError('request_validation should be a boolean value')

        if self.required_user_permissions is not None and isinstance(self.required_user_permissions, str):
            self.required_user_permissions = [self.required_user_permissions]

    def validate_action(self, action):
        """
        Validate that the provided configuration options are valid for the specific Action
        :raises AttributeError:
        """
        if self.__action_validation_completed:
            return

        if action in ['retrieve', 'list', 'destroy']:
            for attr in ['request_serializer', 'request_validation', 'success_status']:
                if getattr(self, attr, None):
                    raise AttributeError(f'{attr} not valid for action {action}')

        if action in ['retrieve', 'list']:
            if self.serializer and self.response_serializer:
                raise AttributeError(f'Only one of serializer or response_serializer are valid for action {action}')

        if action in ['destroy']:
            if self.serializer or self.request_serializer or self.response_serializer:
                raise AttributeError(f'serializers are not valid for action {action}')

        self.__action_validation_completed = True

    def standardize_serializer_properties(self):
        """
        Final serializer options should be in `request_serializer` and `response_serializer` and not in `serializer`.
        If there was an explicit `response_serializer` set, then it is likely different than the request serializer
        (whether set explicitly in configuration or via the fallback default `serializer_class`).  In this case we
        will re-serialize the data in the response using the response_serializer.

        Convert the response_serializer value in to a ResponseSerializers object.  If the provided value is not a
        dictionary, then set the `default` property to the serializer class provided.  If a dictionary was provided,
        ensure the `default` key exists and create the ResponseSerializers object with the provided property/values.

        :raises AttributeError:
        """
        if self.__serializer_standardization_completed:
            return

        if self.serializer:
            self.request_serializer = self.serializer
            self.response_serializer = self.serializer
            self.serializer = None

        elif self.request_serializer or self.response_serializer:
            self.re_serialize_response = True

        if self.response_serializer:
            if not isinstance(self.response_serializer, ActionConfiguration.ResponseSerializers):
                if isinstance(self.response_serializer, dict):
                    self.response_serializer = ActionConfiguration.ResponseSerializers(**self.response_serializer)
                else:
                    self.response_serializer = ActionConfiguration.ResponseSerializers(default=self.response_serializer)

        self.__serializer_standardization_completed = True

    @property
    def raise_validation(self):
        return self.request_validation if self.request_validation is not None else True


class ConfigurableGenericViewSet(GenericViewSet):
    """
    The ConfigurableGenericViewSet class does not provide any actions by default,
    but does include the base set of generic view behavior, as well as the
    logic to handle the configuration via processing ActionConfiguration objects.
    """
    configuration = None
    action_user_permissions = None
    default_required_user_permissions = None

    def __init__(self, **kwargs):
        super(ConfigurableGenericViewSet, self).__init__(**kwargs)

        if issubclass(self.__class__, mixins.MultiSerializerViewSetMixin):
            raise AttributeError(f'Cannot use MultiSerializerViewSetMixin when using ConfigurableGenericViewSet')

        if issubclass(self.__class__, mixins.MultiPermissionViewSetMixin):
            raise AttributeError(f'Cannot use MultiPermissionViewSetMixin when using ConfigurableGenericViewSet')

    def _process_configurations(self):

        if self.configuration is None:
            raise AttributeError(f'{self.__class__.__name__} should include a `configuration` attribute.')

        for action, config in self.configuration.items():
            config.validate_action(action)
            config.standardize_serializer_properties()

            if config.required_user_permissions:
                if self.action_user_permissions is None:
                    self.action_user_permissions = {}
                self.action_user_permissions[action] = config.required_user_permissions

        if self.default_required_user_permissions:
            if self.action_user_permissions is None:
                self.action_user_permissions = {}
            if self.action not in self.action_user_permissions:
                self.action_user_permissions[self.action] = self.default_required_user_permissions

    def get_configuration(self):
        """
        Return the ActionConfiguration for the specific action taking place.  If no defined ActionConfiguration
        exists then return an empty ActionConfiguration.  All ActionConfiguration properties are initialized to None
        """
        self._process_configurations()

        action = self.action

        # PUT and PATCH should use the same configuration
        # pylint: disable=unsupported-membership-test
        if action == 'partial_update' and 'partial_update' not in self.configuration:
            action = 'update'

        # pylint: disable=unsupported-membership-test
        if action in self.configuration:
            return self.configuration[action]  # pylint: disable=unsubscriptable-object

        return ActionConfiguration()

    def get_permissions(self):
        """
        For the given ActionConfiguration, return the defined permission_classes.  If no permission_classes exist
        in the ActionConfiguration, then return the permission_classes as defined on the viewset (which will
        still fall back to the global default setting).
        """
        config = self.get_configuration()
        permission_classes = self.permission_classes

        if config.permission_classes:
            permission_classes = config.permission_classes

        return [permission() for permission in permission_classes]

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.

        This accepts a kwarg `serialization_type` that defaults to REQUEST if not provided.  The associated
        configurable mixins for the default actions provide a serialization_type of RESPONSE in the actions
        where the response may be serialized with a separate class.
        """
        serialization_type = kwargs.pop('serialization_type', mixins.SerializationType.REQUEST)
        serializer_class = self.get_serializer_class(serialization_type)
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    # pylint: disable=arguments-differ
    def get_serializer_class(self, serialization_type=mixins.SerializationType.REQUEST):
        """
        Return the serializer class for the given action and type based on the ActionConfiguration and the
        provided `serialization_type` parameter.  Additionally, if the `format` kwarg is present, then use
        that as an additional lookup field in the ResponseSerializers object.  Failing all this, use the
        super get_serializer_class which should return the value as defined on the ViewSet.
        """
        config = self.get_configuration()

        if serialization_type == mixins.SerializationType.REQUEST and config.request_serializer:
            return config.request_serializer

        if serialization_type == mixins.SerializationType.RESPONSE and config.response_serializer:
            if FORMAT_SUFFIX in self.kwargs and hasattr(config.response_serializer, self.kwargs[FORMAT_SUFFIX]):
                return getattr(config.response_serializer, self.kwargs[FORMAT_SUFFIX])
            return config.response_serializer.default

        return super(ConfigurableGenericViewSet, self).get_serializer_class()


class ConfigurableModelViewSet(mixins.ConfigurableCreateModelMixin,
                               mixins.ConfigurableRetrieveModelMixin,
                               mixins.ConfigurableUpdateModelMixin,
                               mixins.ConfigurableDestroyModelMixin,
                               mixins.ConfigurableListModelMixin,
                               ConfigurableGenericViewSet):
    """
    A viewset that provides *configurable* `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """

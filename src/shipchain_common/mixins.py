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
from rest_framework import status, mixins
from rest_framework.response import Response


class SerializationType:
    REQUEST = 0
    RESPONSE = 1


class MultiSerializerViewSetMixin:
    def get_serializer_class(self):
        """
        Look for serializer class in self.action_serializer_classes, which
        should be a dict mapping action name (key) to serializer class (value),
        i.e.:

        class MyViewSet(MultiSerializerViewSetMixin, ViewSet):
            serializer_class = MyDefaultSerializer
            action_serializer_classes = {
               'list': MyListSerializer,
               'my_action': MyActionSerializer,
            }

            @action
            def my_action:
                ...

        If there's no entry for that action then just fallback to the regular
        get_serializer_class lookup: self.serializer_class, DefaultSerializer.

        Built-in actions:
            create
            retrieve
            update         PUT
            partial_update PATCH
            destroy
            list
        """
        action = self.action

        try:
            # PUT and PATCH should use the same serializers if not separately defined
            if action == 'partial_update' and 'partial_update' not in self.action_serializer_classes:
                action = 'update'

            if 'format' in self.kwargs:
                try:
                    return self.action_serializer_classes[f'{action}.{self.kwargs["format"]}']
                except (KeyError, AttributeError):
                    pass

            return self.action_serializer_classes[action]

        except (KeyError, AttributeError):
            return super(MultiSerializerViewSetMixin, self).get_serializer_class()


class MultiPermissionViewSetMixin:
    def get_permissions(self):
        """
        Look for permission classes in self.action_permission_classes, which
        should be a dict mapping action name (key) to list of permission classes (value),
        i.e.:

        class MyViewSet(MultiPermissionViewSetMixin, ViewSet):
            permission_classes = (HasViewSetActionPermissions,)
            action_permission_classes = {
               'list': (permissions.AllowAny,),
               'my_action': (HasViewSetActionPermissions, isOwner,),
            }

            @action
            def my_action:
                ...

        If there's no entry for that action then just fallback to the regular permission_classes

        Built-in actions:
            create
            retrieve
            update         PUT
            partial_update PATCH
            destroy
            list
        """
        permission_classes = self.permission_classes

        try:
            action = self.action

            # PUT and PATCH should use the same permission classes if not separately defined
            if action == 'partial_update' and 'partial_update' not in self.action_permission_classes:
                action = 'update'

            permission_classes = self.action_permission_classes[action]

        except (KeyError, AttributeError):
            pass

        return [permission() for permission in permission_classes]


class ConfigurableCreateModelMixin(mixins.CreateModelMixin):
    def create(self, request, *args, **kwargs):
        """
        Provide SerializationType to get_serializer, re-serialize response if necessary, change status code if wanted
        """
        config = self.get_configuration()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=config.raise_validation)
        instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        if config.re_serialize_response:
            serializer = self.get_serializer(instance=instance, serialization_type=SerializationType.RESPONSE)

        return Response(serializer.data,
                        status=config.success_status or status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        """Returned the saved instance for later processing"""
        return serializer.save()


class ConfigurableRetrieveModelMixin(mixins.RetrieveModelMixin):
    """
    Retrieve a model instance.  Provide SerializationType to get_serializer
    """
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, serialization_type=SerializationType.RESPONSE)
        return Response(serializer.data)


class ConfigurableUpdateModelMixin(mixins.UpdateModelMixin):
    def update(self, request, *args, **kwargs):
        """
        Provide SerializationType to get_serializer, re-serialize response if necessary, change status code if wanted
        """
        config = self.get_configuration()

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=config.raise_validation)
        updated_instance = self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}  # pylint: disable=protected-access

        if config.re_serialize_response:
            serializer = self.get_serializer(instance=updated_instance, serialization_type=SerializationType.RESPONSE)

        return Response(serializer.data, status=config.success_status or status.HTTP_200_OK)

    def perform_update(self, serializer):
        """Returned the updated instance for later processing"""
        return serializer.save()


class ConfigurableDestroyModelMixin(mixins.DestroyModelMixin):
    """No specific Configurable changes; creating mixin for consistency"""


class ConfigurableListModelMixin(mixins.ListModelMixin):
    """
    List a queryset.  Provide SerializationType to get_serializer
    """
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, serialization_type=SerializationType.RESPONSE)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, serialization_type=SerializationType.RESPONSE)
        return Response(serializer.data)

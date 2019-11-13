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

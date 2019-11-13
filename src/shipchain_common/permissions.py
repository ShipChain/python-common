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


from rest_framework import permissions


class HasViewSetActionPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        Look for list of required FeaturePermissions in view.action_user_permissions, which
        should be a dict mapping action name (key) to FeaturePermission (value),
        i.e.:

        class MyViewSet(HasViewSetActionPermissions, ViewSet):
            permission_classes = (permissions.IsAuthenticated, HasViewSetActionPermissions)
            action_user_permissions = {
                'create': 'my_feature.create_object',
                'retrieve': 'my_feature.view_object',
                'my_action': 'my_feature.special_permission',
            }

            @action
            def my_action:
                ...

        If there's no entry for that action then return True so other Permission checks can run.

        This expects User.has_perm() to be provided by the authentication backend/class

        Built-in actions:
            create
            retrieve
            update         PUT
            partial_update PATCH
            destroy
            list
        """
        if request.user and request.user.is_authenticated:

            if view.action_user_permissions is None:
                return True

            action = view.action

            # PUT and PATCH should use the same permissions if not separately defined
            if action == 'partial_update' and 'partial_update' not in view.action_user_permissions:
                action = 'update'

            try:
                perms = view.action_user_permissions[action]
                if isinstance(perms, str):
                    perms = [perms]
            except (KeyError, AttributeError):
                return True

            return request.user.has_perms(perms)
        return False

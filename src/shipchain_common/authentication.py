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

from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework_simplejwt.models import TokenUser

from .utils import parse_dn


PASSIVE_JWT_AUTHENTICATION = JWTTokenUserAuthentication()


def passive_credentials_auth(jwt):
    if jwt == "":
        raise AuthenticationFailed('No JWT provided with request')
    return PASSIVE_JWT_AUTHENTICATION.get_user(PASSIVE_JWT_AUTHENTICATION.get_validated_token(jwt))


def get_jwt_from_request(request):
    """
    This is for retrieving the decoded JWT from the a request via the simplejwt authenticator.
    """
    if settings.PROFILES_ENABLED and request.user and request.user.is_authenticated:
        return (request.authenticators[-1].get_raw_token(request.authenticators[-1].get_header(request)).decode()
                if request.authenticators else None)
    return None


def is_internal_call(request):
    return ('X_NGINX_SOURCE' in request.META and request.META['X_NGINX_SOURCE'] == 'internal'
            and request.META['X_SSL_CLIENT_VERIFY'] == 'SUCCESS')


class InternalRequest(BasePermission):
    def has_permission(self, request, view):
        if settings.ENVIRONMENT in ('LOCAL', 'INT'):
            return True
        if is_internal_call(request):
            certificate_cn = parse_dn(request.META['X_SSL_CLIENT_DN'])['CN']
            return certificate_cn == f'{self.SERVICE_NAME}.{settings.ENVIRONMENT.lower()}-internal'
        return False


class EngineRequest(InternalRequest):
    SERVICE_NAME = 'engine'


class PermissionedTokenUser(TokenUser):
    """
    This Requires the JWT from Profiles to have been generated with the `permissions` scope
    Override the default class by setting SIMPLE_JWT['TOKEN_USER_CLASS'] = 'path.to.this.class'
    """

    def save(self):
        raise NotImplementedError('Token users have no DB representation')

    def delete(self):
        raise NotImplementedError('Token users have no DB representation')

    def set_password(self, raw_password):
        raise NotImplementedError('Token users have no DB representation')

    def check_password(self, raw_password):
        raise NotImplementedError('Token users have no DB representation')

    def _get_permission_cache_key(self):
        """
        Build a unique cache key for this specific JWT.
        If no `jti`, `at_hash`, or `sub` and `exp`, then return None
        """
        unique_key = self.token.get('jti')

        if not unique_key:
            unique_key = self.token.get('at_hash')

        if not unique_key:
            sub = self.token.get("sub")
            exp = self.token.get("exp")
            if sub and exp:
                unique_key = f'{sub}.{exp}'

        return unique_key

    def _get_permission_cache_life(self):
        """
        Determine cache life from JWT.  If exp or iat are not present, or
        if calculation results in an invalid life, return the fallback_life
        """
        fallback_life = 300

        exp = self.token.get("exp")
        iat = self.token.get("iat")

        if not exp or not iat:
            return fallback_life

        life = exp - iat

        if not life or life <= 0:
            return fallback_life

        return life

    def get_all_permissions(self, obj=None):
        """
        For each Feature/FeaturePermission, build a dot-pathed permission
        These values are cached if we can find a suitable unique key in the token.
        This prevents re-parsing the permissions over the lifetime of this token
        as they will not change until a new token is received
        """
        permissions = None
        unique_key = self._get_permission_cache_key()

        if unique_key:
            permissions = cache.get(unique_key)

        if not permissions:
            features = self.token.get('features')
            if not features:
                return []

            permissions = []
            for feature in features:
                for permission in features[feature]:
                    permissions.append(f'{feature}.{permission}')

            if unique_key:
                cache.set(unique_key, permissions, self._get_permission_cache_life())

        return permissions

    def has_perm(self, perm, obj=None):
        """
        Validate perm is in token feature permissions
        """
        return perm in self.get_all_permissions(obj)

    def has_perms(self, perm_list, obj=None):
        """
        Validate perm_list is in token feature permissions
        """
        return all(self.has_perm(perm, obj) for perm in perm_list)

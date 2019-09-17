from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

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
    if not settings.PROFILES_ENABLED:
        return None
    return (request.authenticators[-1].get_raw_token(request.authenticators[-1].get_header(request)).decode()
            if request.authenticators else None)


def is_internal_call(request):
    return ('X_NGINX_SOURCE' in request.META and request.META['X_NGINX_SOURCE'] == 'internal'
            and request.META['X_SSL_CLIENT_VERIFY'] == 'SUCCESS')


class InternalRequest(BasePermission):
    def has_permission(self, request, view):
        if settings.ENVIRONMENT in ('LOCAL',):
            return True
        if is_internal_call(request):
            certificate_cn = parse_dn(request.META['X_SSL_CLIENT_DN'])['CN']
            return certificate_cn == f'{self.SERVICE_NAME}.{settings.ENVIRONMENT.lower()}-internal'
        return False

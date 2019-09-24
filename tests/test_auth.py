import django
# We run django.setup() in order to auto populate the base django's app models for testing purposes
try:
    django.setup()
except Exception as exc:
    raise exc

import pytest
from django.http.request import HttpRequest
from rest_framework import exceptions

from src.shipchain_common.authentication import EngineRequest, passive_credentials_auth
from src.shipchain_common.test_utils import get_jwt
from src.shipchain_common.utils import random_id

USERNAME = 'fake@shipchain.io'
ORGANIZATION_ID = '00000000-0000-0000-0000-000000000001'


@pytest.fixture()
def username():
    return 'fake@shipchain.io'


@pytest.fixture()
def organization_id():
    return random_id()


@pytest.fixture()
def engine_request():
    return EngineRequest()


def test_passive_jwt_auth(username):
    with pytest.raises(exceptions.AuthenticationFailed):
        passive_credentials_auth('')

    user = passive_credentials_auth(get_jwt(username=username))
    assert user.is_authenticated
    assert not user.is_staff
    assert not user.is_superuser
    assert user.username == 'fake@shipchain.io'
    assert user.token.get('organization_id', None) is None


def test_organization_jwt_auth(username, organization_id):
    user = passive_credentials_auth(get_jwt(username=username, organization_id=organization_id))
    assert user.token.get('organization_id', None) == organization_id


def test_engine_auth_requires_header(engine_request):
    request = HttpRequest()

    assert not engine_request.has_permission(request, {})

    request.META['X_NGINX_SOURCE'] = 'alb'
    assert not engine_request.has_permission(request, {})

    request.META['X_NGINX_SOURCE'] = 'internal'
    with pytest.raises(KeyError):
        engine_request.has_permission(request, {})

    request.META['X_SSL_CLIENT_VERIFY'] = 'NONE'
    assert not engine_request.has_permission(request, {})

    request.META['X_SSL_CLIENT_VERIFY'] = 'SUCCESS'
    with pytest.raises(KeyError):
        engine_request.has_permission(request, {})

    request.META['X_SSL_CLIENT_DN'] = '/CN=engine.h4ck3d'
    assert not engine_request.has_permission(request, {})

    request.META['X_SSL_CLIENT_DN'] = '/CN=profiles.test-internal'
    assert not engine_request.has_permission(request, {})

    request.META['X_SSL_CLIENT_DN'] = '/CN=engine.test-internal'
    assert engine_request.has_permission(request, {})

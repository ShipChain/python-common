from uuid import uuid4

import django
# We run django.setup() in order to auto populate the base django's app models for testing purposes
from rest_framework_simplejwt.utils import aware_utcnow, datetime_to_epoch

try:
    django.setup()
except Exception as exc:
    raise exc

import pytest
from django.http.request import HttpRequest
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import UntypedToken

from src.shipchain_common.authentication import EngineRequest, passive_credentials_auth, PermissionedTokenUser
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


def test_token_user_jti_cache_key():
    """By default, the jti is included in get_jwt and is used as cache key"""
    jwt = get_jwt()
    token = UntypedToken(jwt)
    token_user = PermissionedTokenUser(token)
    assert token_user._get_permission_cache_key() == token_user.token.get('jti')


def test_token_user_at_hash_cache_key():
    """If no jti is included in get_jwt then use at_hash as cache key if exists"""
    jwt = get_jwt(jti=0, at_hash=uuid4().hex)
    token = UntypedToken(jwt)
    token_user = PermissionedTokenUser(token)
    assert token_user._get_permission_cache_key() == token_user.token.get('at_hash')


def test_token_user_sub_exp_cache_key():
    """If no jti or at_hash is included in get_jwt then use {sub}.{exp} as cache key"""
    jwt = get_jwt(jti=0, sub=uuid4().hex)
    token = UntypedToken(jwt)
    token_user = PermissionedTokenUser(token)
    assert token_user._get_permission_cache_key() == f'{token_user.token.get("sub")}.{token_user.token.get("exp")}'


def test_token_user_cache_life():
    jwt = get_jwt()
    token = UntypedToken(jwt)
    token_user = PermissionedTokenUser(token)
    assert token_user._get_permission_cache_life() == 300


def test_token_user_cache_calculated_life():
    iat = datetime_to_epoch(aware_utcnow())
    jwt = get_jwt(exp=iat+15, iat=iat)
    token = UntypedToken(jwt)
    token_user = PermissionedTokenUser(token)
    assert token_user._get_permission_cache_life() == 15


def test_token_user_cache_fallback_life():
    iat = datetime_to_epoch(aware_utcnow())
    jwt = get_jwt(exp=iat+15, iat=iat)
    token = UntypedToken(jwt)
    token.payload['iat'] = None
    token_user = PermissionedTokenUser(token)
    assert token_user._get_permission_cache_life() == 300


@pytest.fixture
def one_feature():
    """Returns feature object response in token, and list of feature permissions"""
    return {'feature': ['permission']}, ['feature.permission']


@pytest.fixture
def many_feature():
    """Returns feature object response in token, and list of feature permissions"""
    return {
        'feature': [
            'permission',
            'permission2',
        ],
        'feature2': [
            'permission',
            'permission2',
        ],
    }, [
        'feature.permission',
        'feature.permission2',
        'feature2.permission',
        'feature2.permission2',
    ]


def test_token_user_get_no_permissions():
    jwt = get_jwt()
    token = UntypedToken(jwt)
    token_user = PermissionedTokenUser(token)
    assert token_user.get_all_permissions() == []


def test_token_user_get_one_permission(one_feature):
    jwt = get_jwt(features=one_feature[0])
    token = UntypedToken(jwt)
    token_user = PermissionedTokenUser(token)
    assert token_user.get_all_permissions() == one_feature[1]


def test_token_user_get_many_permission(many_feature):
    jwt = get_jwt(features=many_feature[0])
    token = UntypedToken(jwt)
    token_user = PermissionedTokenUser(token)
    assert token_user.get_all_permissions() == many_feature[1]


def test_token_user_has_perm(many_feature):
    jwt = get_jwt(features=many_feature[0])
    token = UntypedToken(jwt)
    token_user = PermissionedTokenUser(token)
    assert token_user.has_perm(many_feature[1][2])


def test_token_user_has_perms(many_feature):
    jwt = get_jwt(features=many_feature[0])
    token = UntypedToken(jwt)
    token_user = PermissionedTokenUser(token)
    assert token_user.has_perms(many_feature[1])


def test_token_user_does_not_has_perm(many_feature):
    jwt = get_jwt(features=many_feature[0])
    token = UntypedToken(jwt)
    token_user = PermissionedTokenUser(token)
    assert not token_user.has_perm('not_a_permission')
    assert not token_user.has_perm(many_feature[1][0].split('.')[0])  # doesn't match on just feature
    assert not token_user.has_perm(many_feature[1][0].split('.')[1])  # doesn't match on just permission

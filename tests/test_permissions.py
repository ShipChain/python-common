import pytest
from shipchain_common.permissions import HasViewSetActionPermissions


@pytest.fixture
def test_view():
    class View:
        action = 'list'
        action_permissions = {}
    return View()


@pytest.fixture
def test_user():
    class User:
        is_authenticated = False
        perms = []

        def has_perm(self, perm):
            return perm in self.perms

        def has_perms(self, perm_list):
            return all(self.has_perm(perm) for perm in perm_list)
    return User()


@pytest.fixture
def empty_request():
    class Request:
        user = None
    return Request()


@pytest.fixture
def authed_request(empty_request, test_user):
    class Request:
        user = test_user
        user.is_authenticated = True
    return Request()


def test_no_user(empty_request, test_view):
    """Should be False if no User"""
    test = HasViewSetActionPermissions()
    assert not test.has_permission(empty_request, test_view)


def test_user_not_authenticated(empty_request, test_user, test_view):
    """Should be False if User not authenticated"""
    test = HasViewSetActionPermissions()
    empty_request.user = test_user
    assert not test.has_permission(empty_request, test_view)


def test_view_no_required_permission(authed_request, test_view):
    """Should be True if view lists no action permissions"""
    test = HasViewSetActionPermissions()
    assert test.has_permission(authed_request, test_view)


def test_view_permission_not_for_action(authed_request, test_view):
    """Should be True if view lists action permissions but not for this action"""
    test = HasViewSetActionPermissions()
    test_view.action_permissions = {'create': 'create_permission'}
    assert test.has_permission(authed_request, test_view)


def test_view_permission_missing(authed_request, test_view):
    """Should be False if view lists action permission but it isn't on User"""
    test = HasViewSetActionPermissions()
    test_view.action_permissions = {'list': 'list_permission'}
    assert not test.has_permission(authed_request, test_view)


def test_view_permissions_missing(authed_request, test_view):
    """Should be False if view lists multiple action permissions but all aren't on User"""
    test = HasViewSetActionPermissions()
    test_view.action_permissions = {'list': ['list_permission', 'list_permission2']}
    assert not test.has_permission(authed_request, test_view)


def test_view_permissions_missing_one(authed_request, test_view):
    """Should be False if view lists multiple action permissions but only one is on User"""
    test = HasViewSetActionPermissions()
    authed_request.user.perms.append('list_permission')
    test_view.action_permissions = {'list': ['list_permission', 'list_permission2']}
    assert not test.has_permission(authed_request, test_view)


def test_view_permission_has_it(authed_request, test_view):
    """Should be True if view lists action permission and it's on User"""
    test = HasViewSetActionPermissions()
    authed_request.user.perms.append('list_permission')
    test_view.action_permissions = {'list': 'list_permission'}
    assert test.has_permission(authed_request, test_view)


def test_view_permissions_has_all(authed_request, test_view):
    """Should be True if view lists multiple action permissions and all are on User"""
    test = HasViewSetActionPermissions()
    authed_request.user.perms.append('list_permission')
    authed_request.user.perms.append('list_permission2')
    test_view.action_permissions = {'list': ['list_permission', 'list_permission2']}
    assert test.has_permission(authed_request, test_view)


def test_partial_update_view_permission(authed_request, test_view):
    """Should be True if action is partial, view lists update action permission and User has update"""
    test = HasViewSetActionPermissions()
    authed_request.user.perms.append('update_permission')
    test_view.action = 'partial_update'
    test_view.action_permissions = {'update': 'update_permission'}
    assert test.has_permission(authed_request, test_view)


def test_partial_update_view_update_permission(authed_request, test_view):
    """Should be False if action is partial, view lists partial update action permission and User has update"""
    test = HasViewSetActionPermissions()
    authed_request.user.perms.append('update_permission')
    test_view.action = 'partial_update'
    test_view.action_permissions = {'update': 'update_permission', 'partial_update': 'partial_update_permission'}
    assert not test.has_permission(authed_request, test_view)


def test_partial_update_view_partial_permission(authed_request, test_view):
    """Should be True if action is partial, view lists update action permission and User has update"""
    test = HasViewSetActionPermissions()
    authed_request.user.perms.append('partial_update_permission')
    test_view.action = 'partial_update'
    test_view.action_permissions = {'update': 'update_permission', 'partial_update': 'partial_update_permission'}
    assert test.has_permission(authed_request, test_view)

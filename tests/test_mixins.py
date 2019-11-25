import pytest
from shipchain_common.mixins import MultiSerializerViewSetMixin, MultiPermissionViewSetMixin


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


class FakeViewSet:
    kwargs = {}
    action = 'list'
    serializer_class = 'super'
    action_serializer_classes = {}
    permission_classes = (FakePermission,)
    action_permission_classes = {}

    def get_serializer_class(self):
        return self.serializer_class


class TestMultiSerializerViewSetMixin:

    @pytest.fixture
    def mixin_wrapper(self):
        class WrapperViewSet(MultiSerializerViewSetMixin, FakeViewSet):
            pass
        return WrapperViewSet()
    
    def test_view_no_action_class(self, mixin_wrapper):
        """Should be super class if view lists no action class"""
        assert mixin_wrapper.get_serializer_class() == 'super'

    def test_view_class_not_for_action(self, mixin_wrapper):
        """Should be super class if view lists action class but not for this action"""
        mixin_wrapper.action_serializer_classes = {'create': 'create_class'}
        assert mixin_wrapper.get_serializer_class() == 'super'

    def test_view_class_for_action(self, mixin_wrapper):
        """Should be action class if view lists action class for this action"""
        mixin_wrapper.action_serializer_classes = {'list': 'list_class'}
        assert mixin_wrapper.get_serializer_class() == 'list_class'

    def test_view_class_for_action_with_format(self, mixin_wrapper):
        """Should be formated action class if view lists format action class for this action and format"""
        mixin_wrapper.kwargs['format'] = 'json'
        mixin_wrapper.action_serializer_classes = {'list.json': 'list_json_class'}
        assert mixin_wrapper.get_serializer_class() == 'list_json_class'

    def test_view_class_for_fallback_action_with_format(self, mixin_wrapper):
        """Should be action class if view lists base action class for this action and format"""
        mixin_wrapper.kwargs['format'] = 'json'
        mixin_wrapper.action_serializer_classes = {'list': 'list_class'}
        assert mixin_wrapper.get_serializer_class() == 'list_class'

    def test_view_class_not_for_action_with_format(self, mixin_wrapper):
        """Should be super class if view lists action class but not for this action and format"""
        mixin_wrapper.kwargs['format'] = 'json'
        mixin_wrapper.action_serializer_classes = {'create.json': 'create_class'}
        assert mixin_wrapper.get_serializer_class() == 'super'
    
    def test_update_view_class_for_partial_action(self, mixin_wrapper):
        """Should be update class if action is partial and view lists update action class"""
        mixin_wrapper.action = 'partial_update'
        mixin_wrapper.action_serializer_classes = {'update': 'update_class'}
        assert mixin_wrapper.get_serializer_class() == 'update_class'

    def test_partial_update_view_class_for_action(self, mixin_wrapper):
        """Should be partial class if action is partial and view lists partial and update action class"""
        mixin_wrapper.action = 'partial_update'
        mixin_wrapper.action_serializer_classes = {'update': 'update_class', 'partial_update': 'partial_update_class'}
        assert mixin_wrapper.get_serializer_class() == 'partial_update_class'

    def test_update_view_class_for_partial_action_with_format(self, mixin_wrapper):
        """Should be update class if action is partial and view lists update action class and format"""
        mixin_wrapper.kwargs['format'] = 'json'
        mixin_wrapper.action = 'partial_update'
        mixin_wrapper.action_serializer_classes = {'update.json': 'update_class'}
        assert mixin_wrapper.get_serializer_class() == 'update_class'


class TestMultiPermissionViewSetMixin:

    @pytest.fixture
    def mixin_wrapper(self):
        class WrapperViewSet(MultiPermissionViewSetMixin, FakeViewSet):
            pass
        return WrapperViewSet()

    def test_view_no_action_class(self, mixin_wrapper):
        """Should be default class if view lists no action class"""
        assert mixin_wrapper.get_permissions() == [FakePermission()]

    def test_view_class_not_for_action(self, mixin_wrapper):
        """Should be default class if view lists action class but not for this action"""
        mixin_wrapper.action_permission_classes = {'create': [FakePermission2]}
        assert mixin_wrapper.get_permissions() == [FakePermission()]

    def test_view_class_for_action(self, mixin_wrapper):
        """Should be action class if view lists action class for this action"""
        mixin_wrapper.action_permission_classes = {'list': [FakePermission2]}
        assert mixin_wrapper.get_permissions() == [FakePermission2()]

    def test_view_class_list_for_action(self, mixin_wrapper):
        """Should be all action classes if view lists action classes for this action"""
        mixin_wrapper.action_permission_classes = {'list': [FakePermission2, FakePermission3]}
        assert mixin_wrapper.get_permissions() == [FakePermission2(), FakePermission3()]

    def test_update_view_class_for_partial_action(self, mixin_wrapper):
        """Should be update class if action is partial and view lists update action class"""
        mixin_wrapper.action = 'partial_update'
        mixin_wrapper.action_permission_classes = {'update': [FakePermission2]}
        assert mixin_wrapper.get_permissions() == [FakePermission2()]

    def test_partial_update_view_class_for_action(self, mixin_wrapper):
        """Should be partial class if action is partial and view lists partial and update action class"""
        mixin_wrapper.action = 'partial_update'
        mixin_wrapper.action_permission_classes = {'update': [FakePermission2], 'partial_update': [FakePermission3]}
        assert mixin_wrapper.get_permissions() == [FakePermission3()]

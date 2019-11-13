import pytest
from shipchain_common.views import MultiSerializerViewSetMixin


class FakeViewSet:
    kwargs = {}
    action = 'list'
    serializer_class = 'super'
    serializer_action_classes = {}

    def get_serializer_class(self):
        return self.serializer_class


@pytest.fixture
def mixin_wrapper():
    class WrapperViewSet(MultiSerializerViewSetMixin, FakeViewSet):
        pass
    return WrapperViewSet()


def test_view_no_action_class(mixin_wrapper):
    """Should be super class if view lists no action class"""
    assert mixin_wrapper.get_serializer_class() == 'super'


def test_view_class_not_for_action(mixin_wrapper):
    """Should be super class if view lists action class but not for this action"""
    mixin_wrapper.serializer_action_classes = {'create': 'create_class'}
    assert mixin_wrapper.get_serializer_class() == 'super'


def test_view_class_for_action(mixin_wrapper):
    """Should be action class if view lists action class for this action"""
    mixin_wrapper.serializer_action_classes = {'list': 'list_class'}
    assert mixin_wrapper.get_serializer_class() == 'list_class'


def test_view_class_for_action_with_format(mixin_wrapper):
    """Should be formated action class if view lists format action class for this action and format"""
    mixin_wrapper.kwargs['format'] = 'json'
    mixin_wrapper.serializer_action_classes = {'list.json': 'list_json_class'}
    assert mixin_wrapper.get_serializer_class() == 'list_json_class'


def test_view_class_for_fallback_action_with_format(mixin_wrapper):
    """Should be action class if view lists base action class for this action and format"""
    mixin_wrapper.kwargs['format'] = 'json'
    mixin_wrapper.serializer_action_classes = {'list': 'list_class'}
    assert mixin_wrapper.get_serializer_class() == 'list_class'


def test_view_class_not_for_action_with_format(mixin_wrapper):
    """Should be super class if view lists action class but not for this action and format"""
    mixin_wrapper.kwargs['format'] = 'json'
    mixin_wrapper.serializer_action_classes = {'create.json': 'create_class'}
    assert mixin_wrapper.get_serializer_class() == 'super'


def test_update_view_class_for_partial_action(mixin_wrapper):
    """Should be update class if action is partial and view lists update action class"""
    mixin_wrapper.action = 'partial_update'
    mixin_wrapper.serializer_action_classes = {'update': 'update_class'}
    assert mixin_wrapper.get_serializer_class() == 'update_class'


def test_partial_update_view_class_for_action(mixin_wrapper):
    """Should be partial class if action is partial and view lists partial and update action class"""
    mixin_wrapper.action = 'partial_update'
    mixin_wrapper.serializer_action_classes = {'update': 'update_class', 'partial_update': 'partial_update_class'}
    assert mixin_wrapper.get_serializer_class() == 'partial_update_class'


def test_update_view_class_for_partial_action_with_format(mixin_wrapper):
    """Should be update class if action is partial and view lists update action class and format"""
    mixin_wrapper.kwargs['format'] = 'json'
    mixin_wrapper.action = 'partial_update'
    mixin_wrapper.serializer_action_classes = {'update.json': 'update_class'}
    assert mixin_wrapper.get_serializer_class() == 'update_class'

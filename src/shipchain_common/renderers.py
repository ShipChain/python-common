from rest_framework_json_api import renderers, utils
from rest_framework_json_api.serializers import PolymorphicModelSerializer

from .mixins import SerializationType


def _get_resource_name(context, expand_polymorphic_types=False):
    """
    Return the name of a resource with a special override for ConfigurableGenericViewSet's multiple serializers
    """
    if CGVSJsonRenderer.original_get_resource_name is None:
        raise Exception('original_get_resource_name was not captured')

    view = context.get('view')
    is_response = context.get('response', False)

    try:
        original_view_resource_name = getattr(view, 'resource_name', None)

        # If view.resource_name was set, respect it
        if original_view_resource_name:
            raise AttributeError

        # If view is not a ConfigurableGenericViewSet, don't try to get configurable serializer
        from .viewsets import ConfigurableGenericViewSet
        if not isinstance(view, ConfigurableGenericViewSet):
            raise AttributeError

        serializer = view.get_serializer_class(
            serialization_type=SerializationType.RESPONSE if is_response else SerializationType.REQUEST)

        if expand_polymorphic_types and issubclass(serializer, PolymorphicModelSerializer):
            resource_name = serializer.get_polymorphic_types()
        else:
            resource_name = utils.get_resource_type_from_serializer(serializer)

        # Force the default method to find our serializer at view.resource_name and reset when we're done
        setattr(view, 'resource_name', resource_name)
        # pylint: disable=not-callable
        resource_name = CGVSJsonRenderer.original_get_resource_name(context, expand_polymorphic_types)
        setattr(view, 'resource_name', original_view_resource_name)

        return resource_name

    # For any exceptions above, fallback to original method
    except AttributeError:
        # pylint: disable=not-callable
        return CGVSJsonRenderer.original_get_resource_name(context, expand_polymorphic_types)


class CGVSJsonRenderer(renderers.JSONRenderer):
    """JSONRenderer that is aware of the multiple serializers in ConfigurableGenericViewSet
    This also affects the JSONParser since we are patching method in the util package
    """
    original_get_resource_name = None

    if original_get_resource_name is None:
        original_get_resource_name = utils.get_resource_name
        utils.get_resource_name = _get_resource_name

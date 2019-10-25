from rest_framework_json_api.serializers import ValidationError

def filter_enum(queryset, field, value):
    enum = getattr(queryset.model, field).field.enum
    try:
        enum_value = enum[value.upper()]
    except KeyError:
        raise ValidationError('Invalid device type supplied.')

    queryset = queryset.filter(**{field: enum_value.value})
    return queryset

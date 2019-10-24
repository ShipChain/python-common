from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter


class OptionalSlashRouter(SimpleRouter):
    def __init__(self):
        super(OptionalSlashRouter, self).__init__()
        self.trailing_slash = '/?'


class OptionalSlashNested(NestedSimpleRouter):
    def __init__(self, parent_router, parent_prefix, *args, **kwargs):
        super(OptionalSlashNested, self).__init__(parent_router, parent_prefix, *args, **kwargs)
        self.trailing_slash = '/?'

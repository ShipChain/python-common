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

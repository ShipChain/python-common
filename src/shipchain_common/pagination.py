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

from rest_framework_json_api.pagination import JsonApiPageNumberPagination


class JsonApiPagePagination(JsonApiPageNumberPagination):
    """
    Django Rest Framework JsonApi version 3.0.0 introduces JsonApiPageNumberPagination as base pagination class
    with page query param: 'page[number]' that needs to be overridden here with proper value
    """
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class CustomResponsePagination(JsonApiPagePagination):
    def get_paginated_response(self, data):
        response = super(CustomResponsePagination, self).get_paginated_response(data)
        response.data['data'] = response.data.pop('results')
        return response

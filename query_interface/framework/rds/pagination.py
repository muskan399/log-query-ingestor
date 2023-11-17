"""Custom Paginators"""
from collections import OrderedDict

from rest_framework_json_api.pagination import JsonApiLimitOffsetPagination
from rest_framework.views import Response


class OffsetPagination(JsonApiLimitOffsetPagination):
    """Custom offset paginator to use with an endpoint"""

    def __init__(self):
        self.request = None
        self.offset = None
        self.count = None
        self.limit = None

    def paginate_queryset(self, queryset, request, count):
        """Override pagination to not paginate the queryset since it already is
        """
        self.count = count
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.offset = self.get_offset(request)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []

        return queryset

    def get_paginated_response(self, data):
        """This essentially changes 'results' to 'data'"""
        return Response(
            {
                "data": data,
                "meta": {
                    "pagination": OrderedDict(
                        [
                            ("count", self.count),
                            ("limit", self.limit),
                            ("offset", self.offset),
                        ]
                    )
                },
                "links": OrderedDict(
                    [
                        ("first", self.get_first_link()),
                        ("last", self.get_last_link()),
                        ("next", self.get_next_link()),
                        ("prev", self.get_previous_link()),
                    ]
                ),
            }
        )

from rest_framework.pagination import CursorPagination
from rest_framework.views import APIView
import logging

from .framework.rds.pagination import OffsetPagination

from query_interface.serializers import LogEventsQueryParamsSerializer
from .services.log_events_services import LogEventService

logger = logging.getLogger(__name__)


# Create your views here.
class LogFilterView(APIView):
    allowed_methods = ("GET", "OPTIONS", "HEAD")
    pagination_class = CursorPagination
    # Serializer to validate URL query parameters
    serializer_param = LogEventsQueryParamsSerializer

    def get(self, request):
        self.pagination_class = OffsetPagination
        serializer_param = self.serializer_param(data=request.query_params)
        serializer_param.is_valid(raise_exception=True)
        query_params = serializer_param.validated_data
        logger.debug(
            "[Flow Event]: QueryParams(%s) ", query_params
        )
        logger.debug("Enhanced traffic monitoring called.")
        count, data = LogEventService.list(
            query_params=query_params,
            request=request
        )
        pg_instance = self.pagination_class()
        data = pg_instance.paginate_queryset(data, request, count)
        # Data is already serialized
        return pg_instance.get_paginated_response(data)

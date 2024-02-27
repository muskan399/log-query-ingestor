import re
from django.conf import settings
from datetime import timedelta

from django.contrib.sessions import serializers
from rest_framework import serializers
CHAR_FIELD_MAX_LENGTH = 256


class FilterQueryParamsSerializer(serializers.Serializer):
    """
    Serializer for filter query parameters in Flow events end point
    """
    # Filter corresponds to 'WHERE' clause in SQL.
    # Currently filter on following dimension fields are supported.
    # If more fields are added as filter in query parameter, they
    # should be added here.
    def generate_comparison_fields(self, column_names, field_data_type):
        """
        Dynamically generates comparison fields for the given column names.
        Adds attributes like col_name__nin, col_name__gt, col_name__gte.
        """
        for column_name, column_operators in column_names.items():
            for op in column_operators:
                if op=="__isnull" or field_data_type=="char":
                    self.fields[f"{column_name}{op}"] = serializers.ListField(
                        child=serializers.CharField(max_length=CHAR_FIELD_MAX_LENGTH),
                        required=False)
                elif field_data_type == "integer":
                    self.fields[f"{column_name}{op}"] = serializers.ListField(child=serializers.IntegerField(),
                                                                              required=False)
                else:
                    self.fields[f"{column_name}{op}"] = serializers.ListField(child=serializers.FloatField(),
                                                                              required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define a list of column names to generate comparison fields
        # To append any field in the serializer, use these columns.
        # "" - Filters for values in a given list
        # "__nin" - Filters for values not in a given list
        # "__gt" - Filters for values greater than a specified value
        # "__gte" - Filters for values greater than or equal to a specified value
        # "__lt" - Filters for values less than a specified value
        # "__lte" - Filters for values less than or equal to a specified value
        # "__isnull" - Filters for records where a field is null (has no value)

        float_comparison_columns = {
            # Add more column names as needed
        }
        int_comparison_columns = {

            # Add more column names as needed
        }
        char_comparasion_columns = {
            "level": ["__nin", "__icontains","__nicontains", "__isnull",""],
            "message": ["__nin", "__icontains", "__nicontains", "__isnull", ""],
            "resourceId": ["__nin",""],
            "traceId": ["__nin", ""],
            "spanId": ["__nin", ""],
            "commit": ["__nin",  ""],
            "parentResourceId": ["__nin", ""],
            "project_id": [""]

            # Add more column names as needed
        }
        # Generate comparison fields for the specified columns
        self.generate_comparison_fields(int_comparison_columns, "integer")
        self.generate_comparison_fields(float_comparison_columns, "float")
        self.generate_comparison_fields(char_comparasion_columns, "char")

    class Meta:
        resource_name = "log_events"


class PageQueryParamsSerializer(serializers.Serializer):
    """
    Serializer for page query parameters in Flow Event end point
    """
    # Page corresponds to 'LIMIT' and 'OFFSET' clause of SQL
    # Default offset is 0.

    limit = serializers.IntegerField(
        required=False, default=settings.REST_FRAMEWORK["PAGE_SIZE"]
    )
    offset = serializers.IntegerField(required=False, default=0)

    class Meta:
        resource_name = "log_events"


class LogEventsQueryParamsSerializer(serializers.Serializer):
    """
    Serializer for query parameters in Flow Event end point.
    """
    # Start and end time are mandatory query parameter
    # This will correspond to 'BETWEEN' clause in SQL
    start_time = serializers.DateTimeField(required=True)  # default iso-8601
    end_time = serializers.DateTimeField(required=True)  # default iso-8601

    # 'kind' indicates whether result is a composite number or a timeseries
    # Currently this is not being utilised in the service layer.
    kind = serializers.ChoiceField(choices=["timeseries", "composite"], required=False)

    # This corresponds to 'GROUP BY' clause of SQL.
    # Group_by identifies a list of table dimensions that result
    # needs to be grouped by.
    group_by = serializers.MultipleChoiceField(
        choices=[
            "level",
            "message",
            "resourceId",
            "spanId",
            "commit",
            "parentResourceId",
        ],
        required=False,
    )

    # Field identifies a list of table metrics that should be part
    # of result (mostly be part selected columns in SQL)
    fields = serializers.MultipleChoiceField(
        choices=[

            "project_id",
            "level",
            "message",
            "resourceId",
            "traceId",
            "spanId",
            "commit",
            "parentResourceId",
            "timestamp",
            "count"
        ],
        required=True,
    )

    # This corresponds to ASC/DESC clause of SQL.
    # List of table that support ordering. This should be subset of
    # fields specified in 'fields' parameter.
    sort = serializers.MultipleChoiceField(
        choices=[
            "count",
            "level",
            "message",
            "timestamp",
            "-count",
            "-level",
            "-message",
            "-timestamp",
        ],
        required=False,
    )

    # Filter identifies table dimensions that should be used to
    # filter the result (mostly be part of WHERE clause in SQL)
    filters = FilterQueryParamsSerializer(required=True)

    # This mostly corresponds to LIMIT and OFFSET in SQL
    page = PageQueryParamsSerializer(required=False)

    class Meta:
        resource_name = "log_events"

    def __init__(self, data, **kwargs):
        """
        preprocess query parameter before serialization
        """
        # To save validated query params

        self.query_params = {}

        filter_table = {}
        search_table = {}
        page_table = {}

        if data is not {}:
            for k, v in data.lists():
                if k in [
                    "start_time",
                    "end_time",
                    "kind",
                    "interval",
                    "page[offset]",
                    "page[limit]",
                    "filter[parent_account]",
                ]:
                    # Some query params should have only one value,
                    # pick last one
                    v = data[k]
                else:
                    # Some query param can have multiple values and
                    # can appear multiple times,for example
                    # ?abc=2,3,4&abc=8
                    # This is represented in QueryDict as
                    # {'abc': ['2,3,4', '8']}
                    # Convert it to simple
                    # {'abc': {'2', '3', '4', '8'}}
                    # This will help to validate individual values
                    # in list and remove duplicates.
                    v = {y for x in v for y in x.split(",")}

                # JSON API recommends certain query paramaters like
                # 'filter', 'search' and 'page' be in form
                #  - /comments?filter[router_id]=12235
                #  - /comments?filter[account_id]=235&filter[router_id]=12235,3221
                #  - /comments?page[offset]=5
                #  - /comments?page[limit]=6
                #  - /comments?search[app_name,category_name]=abc,def,ghi
                #
                # Use of brackets in paramater key does not help with
                # serialization. Change the query paramater raw data
                # to following before starting
                # {
                #   "filters": {
                #       "account_id": [235],
                #       "router_id": [12235, 3221],
                #       "src_site_name": {"neg": "site1"}
                #   },
                #   "search": {
                #       "app_name": [abc,def,ghi],
                #       "category_name": [abc,def,ghi],
                #   },
                #   "page": {"limit": 6, "offset": 5}
                # }
                filter_arg = self.parse_filter(k, predicate="filter")

                # Generates structure like
                # { "filter" :
                #       {
                #           "latency_client": {"gt": 6.3, "lt": 10 },
                #            "src_site_name": {"eq": "site1"}
                #       }
                #  }
                if filter_arg:
                    # filter parameter
                    filter_table.update({filter_arg: v})

                elif k == "page[offset]":
                    # page parameter
                    page_table["offset"] = v
                elif k == "page[limit]":
                    page_table["limit"] = v
                else:
                    self.query_params[k] = v

        if filter_table:
            self.query_params["filters"] = filter_table
        if page_table:
            self.query_params["page"] = page_table

        # Query paramater has been preprocessed, call base serializer
        super().__init__(data=self.query_params, **kwargs)

    def validate(self, data):
        """ validate query params """
        # check start time isn't greater than end time
        if data["start_time"] > data["end_time"]:
            raise serializers.ValidationError(
                detail="End time must be greater than start time"
            )

        # fields and group_by parameters determine columns returned
        # by SQL. Value in 'sort' and 'search' parameter must be
        # present in either one of those.
        col_fields = set().union(data.get("fields", set()), data.get("group_by", set()))
        remove_prefix = lambda x: x[1:] if x.startswith("-") else x
        if not set(map(remove_prefix, data.get("sort", set()))) <= col_fields:
            raise serializers.ValidationError(
                detail=f"Sort columns must be in fields or group_by"
            )

        # filter[bytes_in__gt]=23,42, this statement doesn't make any sense,
        # so length should be 1
        # Add more column names as needed]
        op_list = ["__gt", "__gte", "__lt", "__lte"]

        for key, value in data.get("filters").items():
            if "__isnull" in key:
                if value[0].lower() not in ["true", "false"] or len(value) > 1:
                    raise serializers.ValidationError(
                        detail=f"Is Null cannot hold values other than bool- {key}:{value}"
                    )

            if "__" in key and (key[key.index("__"):] in op_list):
                if len(value) > 1:
                    raise serializers.ValidationError(
                        detail=f"Comparative operation cannot hold more than 1 value- {key}:{value}"
                    )

        group_by_col_fields = data.get("group_by")
        invalid_keys = []

        if group_by_col_fields:
            for key in col_fields:
                if key != "count" and key not in group_by_col_fields:
                    invalid_keys.append(key)

        if invalid_keys:
            raise serializers.ValidationError(
                detail=f"With Group-By, field cannot hold any columns other than the grouped_column and count-field: "
                       f"{', '.join(invalid_keys)}, group_by: {group_by_col_fields}"
            )

        return data

    def parse_filter(self, arg, predicate="filter"):
        """ parse an attribute from a filter arg
        arg = 'filter[foo]' will return foo
        arg = 'search[foo,bar]' will return foo,bar

        Args:
         arg: the arg to parse
         predicate: the predicate, default to filter

        Returns:
         the results of the regex search
        """
        match = re.search("{0}\[(.+?)\]".format(predicate), arg)
        if match:
            return match.group(1)
        else:
            return None

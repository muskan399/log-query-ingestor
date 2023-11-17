import logging
import uuid

import psycopg2
from psycopg2 import sql
from collections import OrderedDict
from django.core.exceptions import EmptyResultSet
import pymysql
from sqlalchemy import create_engine, text

from log_ingestor_system import settings

logger = logging.getLogger(__name__)


class EnhancedLogEventsQueryBuilder(object):
    """
    Build SQL query for log events endpoint based on query
    parameters
    """

    def __init__(self, request, table, query_params):
        self.request = request
        self.table = table
        self.query_params = query_params
        self.values = []

    def compose_total_count_query(self):
        """
        Return SQL query for calculating total count

        For endpoints with only filter condition this type of query will be generated
        SELECT count(*)
        FROM log_data
        WHERE created_at BETWEEN %s AND %s
        AND date_time BETWEEN %s AND %s
        AND project_id IN (%s)

        For endpoints with filter + groupby this type of query will be generated
        SELECT count(*) FROM (
            SELECT count(*) FROM log_data
            WHERE created_at BETWEEN %s AND %s
            AND timestamp BETWEEN %s AND %s
            AND message IN (%s)
        GROUP BY level
        ) AS Z
        """
        groupby = self._get_groupby()
        q = "SELECT {} FROM {} WHERE {}".format(
            "count(*)",
            self.table,
            " AND ".join(self._get_filters()),
        )
        if groupby:
            q = "SELECT count(*) FROM ({} GROUP BY {}) AS Z".format(q, ", ".join(groupby))

        return q, self.values

    def compose(self):
        """
        Return SQL query

        For log event endpoint, all DB SQL queries follow same structure
        shown below. The differences are mainly in select column
        names, where clause filters and group by fields.
        These variables are controlled by query parameters
        """
        if "final_action" in self.query_params["fields"]:
            self.query_params["fields"].update(["rule_action", "idps_action"])

        q = "SELECT {} FROM {} WHERE {}".format(
            ", ".join(self._get_columns()),
            self.table,
            " AND ".join(self._get_filters()),
        )

        # add groupby, if needed
        groupby = self._get_groupby()
        if groupby:
            q = "{} GROUP BY {}".format(q, ", ".join(groupby))

        # add orderby, if needed
        orderby = self._get_orderby()
        if orderby:
            q = "{} ORDER BY {}".format(q, ", ".join(orderby))

        if "page" in self.query_params:
            q = "{} LIMIT {} OFFSET {}".format(
                q, "%s", "%s"
            )

            self.values.append(self.query_params["page"]["limit"])
            self.values.append(self.query_params["page"]["offset"])
        return q, self.values

    def _get_columns(self):
        """
        Translate fields required in result to corresponding column
        names in the SQL SELECT statement
        """
        mapping = {
            "count": "count(*) as count",
            "level": "level",
            "message": "message",
            "resourceId": "resourceId",
            "traceId": "traceId",
            "spanId": "spanId",
            "commit": "commit",
            "parentResourceId": "parentResourceId",
            "timestamp": "timestamp",
            "projectId": "projectId"

        }

        # All groupby fields are part of column names in SELECT
        for x in self.query_params.get("group_by") or set():
            self.query_params["fields"].add(x)

        # construct the column name list in SQL SELECT
        return [mapping[v] for v in self.query_params["fields"] if v in mapping]

    def _get_filters(self):
        """
        fields for SQL WHERE clause based on 'filters' in query params
        """
        # map names is query parameter to table dimensions
        mapping = {
            "count": "count(*) as count",
            "projectId": "projectId",
            "level": "level",
            "message": "message",
            "resourceId": "resourceId",
            "traceId": "traceId",
            "spanId": "spanId",
            "commit": "commit",
            "parentResourceId": "parentResourceId",
            "timestamp": "timestamp",
        }

        clause = []
        start_time = self.query_params["start_time"]
        end_time = self.query_params["end_time"]
        null_delimiter = "null"
        int_columns = ["src_port", "dst_port", "bytes_in", "bytes_out", "packets_in", "packets_out"]
        float_columns = ["latency_client", "latency_server"]
        check_is_empty = True

        # Passing the values, for parametrised query
        self.values.append(start_time)
        self.values.append(end_time)
        clause.append("timestamp between %s and %s")

        # list of possible operators.
        # Used In and Not In, since we can have item of tuple also, e.g src_site_name in ("site1", site2")
        operator_mapping = {
            "__in": "IN",
            "__nin": "NOT IN",
            "__lt": "<",
            "__lte": "<=",
            "__gt": ">",
            "__gte": ">=",
            "__icontains": "LIKE",
            "__nicontains": "NOT LIKE",
        }
        # For empty and not empty, different structure is used.
        # filter[col_name__isnull]=True, IS NULL is used.
        # filter[col_name__isnull]=FALSE, IS NOT NULL is used.
        # rest is based on filter fields


        for dimension, values in self.query_params["filters"].items():
            if not values:
                # no filter values specified, cannot run query
                raise EmptyResultSet

            op = "__in"
            if "__" in dimension:
                # Retrieve the operator e.g. __nin, __gt
                op = dimension[dimension.index("__"):]
                # Retrieve the dimension, get "src_site_name" from "src_site_name__nin"
                dimension = dimension.split("__")[0]
            if dimension in mapping:
                if values[0] == null_delimiter:
                    clause.append("{} {}".format(mapping[dimension], "IS NULL", values))
                elif op == "__isnull":
                    if dimension in int_columns or dimension in float_columns:
                        check_is_empty = False

                    condition_function = self.__handle_is_null_and_empty_condition if values[
                                                                                          0].lower() == "true" else self.__handle_is_not_null_and_empty_condition
                    condition_function(clause, mapping[dimension], check_is_empty)

                elif op in ["__icontains", "__nicontains"]:
                    for search_text in values:
                        self.values.append(f"%{search_text}%")
                        clause.append(
                            "{} {} {}".format(
                                mapping[dimension],
                                operator_mapping[op],
                                # make sure search text is properly escaped,
                                "%s"
                            )
                        )

                else:
                    self.values.extend(values)
                    values = ", ".join("%s" for _ in values)
                    clause.append(
                        "{} {} ({})".format(mapping[dimension], operator_mapping[op], values))
        return clause

    def _get_groupby(self):
        """
        fields for SQL GROUP BY clause based on 'group_by' in query params
        """
        # map names is query parameter to table dimensions
        mapping = {
            "level": "level",
            "message": "message",
            "resourceId": "resourceId",
            "traceId": "traceId",
            "spanId": "spanId",
            "commit": "commit",
            "parentResourceId": "parentResourceId",
        }

        # if created_at is in group_by, it should be the first one
        gb = (
            ["created_at"]
            if "created_at" in self.query_params.get("group_by", {})
            else []
        )

        # join all groupby fields. In order to keep the ordering of
        # fields, use query param from request
        if self.query_params.get("group_by"):
            for v in self.query_params.get("group_by"):
                gb.extend([x for x in v.split(",")])
        else:
            for v in self.request.query_params.getlist("group_by"):
                gb.extend([x for x in v.split(",")])

        # remove any duplicates while preserving order
        gb = list(OrderedDict.fromkeys(gb))

        return [mapping[x] for x in gb if x in mapping]

    def _get_orderby(self):
        """
        fields for SQL ORDER BY clause based on 'sort' query param
        """
        # map names is query parameter to table fields
        mapping = {
            "level": "level ASC",
            "message": "message ASC",
            "timestamp": "timestamp ASC",
            "-level": "level DESC",
            "-message": "resourceId DESC",
            "-timestamp": "timestamp DESC",
        }

        # join all orderby fields. In order to keep the ordering of
        # fields, use the param from request
        ob = [
            x for v in self.request.query_params.getlist("sort") for x in v.split(",")
        ]

        # remove any duplicates while preserving order
        ob = list(OrderedDict.fromkeys(ob))

        if len(ob) == 0:
            if "count" in self.query_params["fields"]:
                ob.append("-count")
            else:
                ob.append("-timestamp")

        return [mapping[x] for x in ob if x in mapping]

    def __handle_is_null_and_empty_condition(self, clause, col_name, check_is_empty=True):
        if check_is_empty:
            clause.append("({} {} {} {} {})".format(col_name, "IS NULL OR", col_name, "=",
                                                    "%s"))
            self.values.append("")
        else:
            clause.append(
                "({} {})".format(col_name, "IS NULL"))

    def __handle_is_not_null_and_empty_condition(self, clause, col_name, check_is_empty=True):
        if check_is_empty:
            clause.append(
                "({} {} {} {} {})".format(col_name, "IS NOT NULL OR", col_name, "!=",
                                          "%s"))
            self.values.append("")
        else:
            clause.append(
                "({} {})".format(col_name, "IS NOT NULL"))


class LogEventService:
    @staticmethod
    def list(
            request,
            query_params
    ):
        """This method composes a query, executes it on the db and
        returns the total_count and formatted result.

        Params:
            request: the request object.
            query_params: serialized query params.

        Returns:
            the total count and formatted(serialized) result.
        """

        fact_table = LogEventService._get_fact_table()
        fields = query_params["fields"].copy()
        try:
            total_count_qb, total_count_params = EnhancedLogEventsQueryBuilder(request, fact_table,
                                                                               query_params).compose_total_count_query()
            qb, params = EnhancedLogEventsQueryBuilder(request, fact_table, query_params).compose()
            logger.debug("[Log Event]: QueryBuilder: %s", qb)
            print(query_params)
            print(qb)
        except EmptyResultSet:
            # SQL query won't return any result
            header = []
            result = []
            total_count_result = (0)
        else:
            # Replace these with your database connection details
            # database_url = "postgresql://admin:12345678@log-store.cdmwahb69xvs.ap-south-1.rds.amazonaws.com/log_store"

            # # Use the cursor to execute the query

            cursor = get_connection().cursor()
            cursor.execute(total_count_qb, total_count_params)
            total_count_result = cursor.fetchall()[0]

            cursor.execute(qb, params)

            # Fetch the header (column names)
            header = [column[0] for column in cursor.description]

            # Fetch all rows
            rows = cursor.fetchall()

        # Format and postprocess data returned by DB
        result = LogEventService._format_result(header, rows, fields)
        print("Response is: ", result, total_count_result)
        return total_count_result[0], result

    @staticmethod
    def _format_result(header, result, fields):
        """
        Format and serialize result for DB.

        Params:
            header: list of columns that will be returned
            result: list of output from the db.

        Returns:
            returns the total_count(without pagination) and result
            in this format {"type": "log_events", "attributes": {}, "id": ""}
        """

        # Formatting the result as per JSONAPI format.
        def fn(attributes):
            return {"type": "log_events", "attributes": attributes, "id": uuid.uuid4()}

        ret = []
        total_count = 0

        # If the column name used by UI don't match with the database column name,
        # then mention the mapping here, else it will use the database column name only.
        ui_header = {
            "message": "log_message",
        }

        # Mapping the database header with the UI headers as it is possible both are using different names.
        header = [ui_header.get(col, col) for col in header]

        # Apply the function to each row
        ret = [fn(dict(zip(header, row))) for row in result]

        logger.info("[Log Event]: Total count: %s\nResult: %s", total_count, ret)
        return ret

    @staticmethod
    def _get_fact_table():
        """Returns the log_data table."""
        return "log_data";


def get_connection(conf="default"):
    """
    Get a connection for the given DB configuration.
    conf: db index in settings.DATABASES
    """
    if conf not in settings.DATABASES:
        # database information not present. should not happen
        return None

    conn = pymysql.connect(
        user=settings.DATABASES[conf].get("USER"),
        host=settings.DATABASES[conf].get("HOST"),
        port=settings.DATABASES[conf].get("PORT"),
        database=settings.DATABASES[conf].get("NAME"),
        password=settings.DATABASES[conf].get("PASSWORD"),
    )
    return conn

import requests


def get_filter_type():
    while True:
        filter_type = input("Enter filter type (EQUALS, NOT EQUALS, CONTAINS, NOT CONTAINS): ")
        if not filter_type or filter_type.upper() in ['EQUALS', 'NOT EQUALS', 'CONTAINS', 'NOT CONTAINS']:
            return filter_type.upper()
        print("Invalid filter type. Please enter a valid filter type.")


def map_filter_type(filter_type):
    mapping = {
        'EQUALS': 'in',
        'NOT EQUALS': 'nin',
        'CONTAINS': 'icontains',
        'NOT CONTAINS': 'nicontains',
    }
    return mapping.get(filter_type, 'in')  # Default to 'in' if not found


api_url = 'http://localhost:3000/query/filter/'

print("\n=============================================================\nHello! Use this CLI to filter,search,"
      "sort and groupby\n=============================================================\n")
# Get user input for parameters with default values
start_time = input("Enter start time (e.g., 2020-02-01T00:00:00) [Default: 2020-02-01T00:00:00]: ") or '2020-02-01T00:00:00'
end_time = input("Enter end time (e.g., 2020-02-05T00:00:00) [Default: 2024-02-05T00:00:00]: ") or '2024-02-05T00:00:00'
# Get group_by from the user
group_by = input("Enter group_by (e.g., level) [Press Enter to skip]: ") or None
if not group_by:
    fields = input("Enter fields (e.g., message,level) [Default: message,level,resourceId,traceId,spanId,commit,"
                   "parentResourceId,timestamp]: ") or ('message,level,resourceId,traceId,spanId,commit,'
                                                        'parentResourceId,timestamp')
    sort = input("Enter sort (e.g., timestamp) [Default: timestamp]: ") or 'timestamp'

else:
    fields = group_by+",count"
    sort = input("Enter sort (e.g., count) [Default: count(with groupby)]: ") or 'count'

page_limit = input("Enter page[limit] [Default: 10]: ") or '10'

# Get filters from the user
filters = {}
project_id = input("Enter the project id [Default: 1]: ") or '1'
filters["filter[project_id]"]=project_id
while True:
    filter_name = input("\nEnter filter name (or press Enter to finish):"
                        "\nAllowed filters are:"
                        "\n1. level(equals,not equals, contains, not contains)"
                        "\n2. message(equals, not equals, contains, not contains)"
                        "\n3. resourceId(equals, not equals)"
                        "\n4. traceId(equals, not equals)"
                        "\n5. spanId(equals, not equals)"
                        "\n6. commit(equals, not equals)"
                        "\n7. parentResourceId(equals, not equals)\n"
                        )
    if not filter_name:
        break
    filter_type = get_filter_type()
    filter_value = input(f"Enter filter value for {filter_name} [{filter_type}]: ") or ''
    filter_suffix = map_filter_type(filter_type)
    if filter_suffix=="in":
        filters[f'filter[{filter_name}]'] = filter_value
    else:
        filters[f'filter[{filter_name}__{filter_suffix}]'] = filter_value

# Construct the parameters
params = {
    'start_time': start_time,
    'end_time': end_time,
    'fields': fields,
    **filters,  # Add dynamic filters
    'sort': sort,
    'group_by': group_by,
    'page[limit]': page_limit,
}

# Make the API call
response = requests.get(api_url, params=params)

if response.status_code == 200:
    data = response.json()["data"]
    print("API call successful(Note: Records are paginated)")
    for record in data:
        print(record["type"],":",record["attributes"])

else:
    print(f"API call failed. Status code: {response.status_code}, Error: {response.text}")

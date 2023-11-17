<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/github_username/repo_name">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Log Ingestor & Query Builder</h3>

  <p align="center">
    This is a Django based project which consists of 2 apps for log ingestion and query evaluation. For the log ingestion RDS is used.
    <br />
    
  </p>
</div>

<br>
<br>
<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project
It is a log ingestor system that can efficiently handle vast volumes of log data, and offer a simple interface for querying this data using full-text search or specific field filters.






### Built With
* Django
* RDS


<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

#### 1. Install Python
Install ```python-3(python 3.10)``` and ```python-pip(pip 23.3.1 )```. Follow the steps from the below reference document based on your Operating System.
Reference: [https://docs.python-guide.org/starting/installation/](https://docs.python-guide.org/starting/installation/)

#### 2. Install MySQL
Install ```mysql-8.0.35```. Follow the steps form the below reference document based on your Operating System.
Reference: [https://dev.mysql.com/doc/refman/5.5/en/](https://dev.mysql.com/doc/refman/5.5/en/)
#### 3. Setup virtual environment
```bash
# Install virtual environment
sudo pip install virtualenv

# Make a directory
mkdir envs

# Create virtual environment
virtualenv ./envs/

# Activate virtual environment
source envs/bin/activate
```
#### 5. Install requirements
```bash
cd november-2023-hiring-muskan399/
pip install -r requirements.txt
```
#### 7. Edit project settings: Note currently it already has config for RDS.
```bash
# open settings file
vim log_ingestor_system/settings.py

# Edit Database configurations with your MySQL configurations.
# Search for DATABASES section.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'world',
        'USER': '<mysql-user>',
        'PASSWORD': '<mysql-password>',
        'HOST': '<mysql-host>',
        'PORT': '<mysql-port>',
    }
}
# save the file
```
#### 8. Run the server
```bash
# Make migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Run the server
python manage.py runserver

# your server is up on port 3000
```

### RDS Table structure and indexes
1. Database name: log_store
2. Table name: log_data
3. Table structure:
```
+-------+-------------------------+----------------+----------------------------+---------------------------+----------+-----------+------------------+-----------+
| level | message                 | resourceId     | timestamp                  | traceId                   | spanId   | commit    | parentResourceId | projectId |
+-------+-------------------------+----------------+----------------------------+---------------------------+----------+-----------+------------------+-----------+
| error | Server Error            | server-1234675 | 2022-12-16 08:00:00.000000 | abc-qddyz-32334           | span-456 | 5e5342f   | server-0987      |           |
| error | Failed to connect to DB | server-1234675 | 2023-12-16 08:00:00.000000 | abc-xyz-123               | span-456 | 5e5342f   | server-0987      | 1         |
| error | Server Error            | server-1234675 | 2023-12-16 08:00:00.000000 | abc-xyz-32334             | span-456 | 5e5342f   | server-0987      | 1         |
| info  | Successfully updated    | server-1234675 | 2022-12-11 08:00:00.000000 | abcd-123                  | span-123 | 21cds342f | server-1         |           |
| info  | Resource Created        | server-1234675 | 2022-12-16 08:00:00.000000 | rfvgrgc-qddyz-32334       | span-456 | 5e5342f   | server-0987      |           |
| info  | Successfully updated    | server-1234675 | 2022-12-16 08:00:00.000000 | rfvgrgc-qdfddddddyz-32334 | span-456 | 5e5342f   | server-0987      |           |
+-------+-------------------------+----------------+----------------------------+---------------------------+----------+-----------+------------------+-----------+
```
4. Indexes on log_data:
* Note: There is a `composite index on timestamp and projectId`, since in every query these 2 values will be compulsory added in filters.
* I have added 1 extra attribute for projectId so that we have data isolation, so that user can see data from authorised project only, further we can add a security layer based on this projectId, for now we can avoid it also and consider there is just `index on timestamp`.
```
mysql> SHOW INDEX FROM log_data;
+----------+------------+-------------------------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+
| Table    | Non_unique | Key_name                | Seq_in_index | Column_name | Collation | Cardinality | Sub_part | Packed | Null | Index_type | Comment | Index_comment | Visible | Expression |
+----------+------------+-------------------------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+
| log_data |          0 | PRIMARY                 |            1 | traceId     | A         |           6 |     NULL |   NULL |      | BTREE      |         |               | YES     | NULL       |
| log_data |          1 | idx_timestamp_projectId |            1 | timestamp   | A         |           3 |     NULL |   NULL |      | BTREE      |         |               | YES     | NULL       |
| log_data |          1 | idx_timestamp_projectId |            2 | projectId   | A         |           3 |     NULL |   NULL |      | BTREE      |         |               | YES     | NULL       |
+----------+------------+-------------------------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+
```
5. Steps to connect to RDS:
* Connect to AWS RDS using mysql client.
```mysql
 mysql -h log-store.cdmwahb69xvs.ap-south-1.rds.amazonaws.com -u admin -p log_store
```
Password: 12345678

* Go to log_store database;
```
USE log_store;
SELECT * FROM log_data;
```

### Log Ingestion
Send a POST request to  `http://localhost:3000/ingest/`
   
``` sh
curl -X POST -H "Content-Type: application/json" -d '{
  "level": "info",
  "message": "Successfully updated",
  "resourceId": "server-1234675",
  "timestamp": "2022-12-11T08:00:00Z",
  "traceId": "abcd-123",
  "spanId": "span-123",
  "commit": "21cds342f",
  "metadata": {"parentResourceId": "server-1"}
}' http://localhost:3000/ingest/
  ```
Response will be:
```
{"status": "success", "message": "Log ingested successfully"}
```

### Query Interface
Allowed Operations:
```* EQUALS: level, message, resourceId, traceId, spanId, commit, parentResourceId
* NOT EQUALS: level, message, resourceId, traceId, spanId, commit, parentResourceId
* CONTAINS: level, message
* NOT CONTAINS: level, message
* SORT: timestamp, level, message
* GROUPBY: level, message
* BETWEEN(Timerange)
```
Use this script to open the cmd line cli.
```
python3 managment/command_line_cli.py
```
<details>
  <summary>With all the default values for filter, time and sort</summary>
  
 ```
 =============================================================
Hello! Use this CLI to filter,search,sort and groupby
=============================================================

Enter start time (e.g., 2020-02-01T00:00:00) [Default: 2020-02-01T00:00:00]: 
Enter end time (e.g., 2020-02-05T00:00:00) [Default: 2024-02-05T00:00:00]: 
Enter group_by (e.g., level) [Press Enter to skip]: 
Enter fields (e.g., message,level) [Default: message,level,resourceId,traceId,spanId,commit,parentResourceId,timestamp]: 
Enter sort (e.g., timestamp) [Default: timestamp]: 
Enter page[limit] [Default: 10]: 
Enter the project id [Default: 1]: 

Enter filter name (or press Enter to finish):
Allowed filters are:
1. level(equals,not equals, contains, not contains)
2. message(equals, not equals, contains, not contains)
3. resourceId(equals, not equals)
4. traceId(equals, not equals)
5. spanId(equals, not equals)
6. commit(equals, not equals)
7. parentResourceId(equals, not equals)

API call successful(Note: Records are paginated)
log_events : {'parentResourceId': 'server-1', 'idps_message': 'Successfully updated', 'level': 'info', 'resourceId': 'server-1234675', 'traceId': 'abcd-123', 'timestamp': '2022-12-11T08:00:00', 'spanId': 'span-123', 'commit': '21cds342f'}
log_events : {'parentResourceId': 'server-0987', 'idps_message': 'Server Error', 'level': 'error', 'resourceId': 'server-1234675', 'traceId': 'abc-qddyz-32334', 'timestamp': '2022-12-16T08:00:00', 'spanId': 'span-456', 'commit': '5e5342f'}
log_events : {'parentResourceId': 'server-0987', 'idps_message': 'Resource Created', 'level': 'info', 'resourceId': 'server-1234675', 'traceId': 'rfvgrgc-qddyz-32334', 'timestamp': '2022-12-16T08:00:00', 'spanId': 'span-456', 'commit': '5e5342f'}
log_events : {'parentResourceId': 'server-0987', 'idps_message': 'Successfully updated', 'level': 'info', 'resourceId': 'server-1234675', 'traceId': 'rfvgrgc-qdfddddddyz-32334', 'timestamp': '2022-12-16T08:00:00', 'spanId': 'span-456', 'commit': '5e5342f'}
log_events : {'parentResourceId': 'server-0987', 'idps_message': 'Failed to connect to DB', 'level': 'error', 'resourceId': 'server-1234675', 'traceId': 'abc-xyz-123', 'timestamp': '2023-12-16T08:00:00', 'spanId': 'span-456', 'commit': '5e5342f'}
log_events : {'parentResourceId': 'server-0987', 'idps_message': 'Server Error', 'level': 'error', 'resourceId': 'server-1234675', 'traceId': 'abc-xyz-32334', 'timestamp': '2023-12-16T08:00:00', 'spanId': 'span-456', 'commit': '5e5342f'}

 ```
  
</details>
<details>
  <summary>With Filters(Equals, Contains, timerange): start_time= 2021-01-01T00:00:00  and end_time= 2024-01-01T00:00:00 and filter[level]=error and filter[message__icontains]=ser and sort=timestamp(asc)</summary>
  
 ```
 =============================================================
Hello! Use this CLI to filter,search,sort and groupby
=============================================================

Enter start time (e.g., 2020-02-01T00:00:00) [Default: 2020-02-01T00:00:00]: 
Enter end time (e.g., 2020-02-05T00:00:00) [Default: 2024-02-05T00:00:00]: 
Enter group_by (e.g., level) [Press Enter to skip]: 
Enter fields (e.g., message,level) [Default: message,level,resourceId,traceId,spanId,commit,parentResourceId,timestamp]: 
Enter sort (e.g., timestamp) [Default: timestamp]: 
Enter page[limit] [Default: 10]: 
Enter the project id [Default: 1]: 

Enter filter name (or press Enter to finish):
Allowed filters are:
1. level(equals,not equals, contains, not contains)
2. message(equals, not equals, contains, not contains)
3. resourceId(equals, not equals)
4. traceId(equals, not equals)
5. spanId(equals, not equals)
6. commit(equals, not equals)
7. parentResourceId(equals, not equals)

API call successful(Note: Records are paginated)
log_events : {'parentResourceId': 'server-1', 'idps_message': 'Successfully updated', 'level': 'info', 'resourceId': 'server-1234675', 'traceId': 'abcd-123', 'timestamp': '2022-12-11T08:00:00', 'spanId': 'span-123', 'commit': '21cds342f'}
log_events : {'parentResourceId': 'server-0987', 'idps_message': 'Server Error', 'level': 'error', 'resourceId': 'server-1234675', 'traceId': 'abc-qddyz-32334', 'timestamp': '2022-12-16T08:00:00', 'spanId': 'span-456', 'commit': '5e5342f'}
log_events : {'parentResourceId': 'server-0987', 'idps_message': 'Resource Created', 'level': 'info', 'resourceId': 'server-1234675', 'traceId': 'rfvgrgc-qddyz-32334', 'timestamp': '2022-12-16T08:00:00', 'spanId': 'span-456', 'commit': '5e5342f'}
log_events : {'parentResourceId': 'server-0987', 'idps_message': 'Successfully updated', 'level': 'info', 'resourceId': 'server-1234675', 'traceId': 'rfvgrgc-qdfddddddyz-32334', 'timestamp': '2022-12-16T08:00:00', 'spanId': 'span-456', 'commit': '5e5342f'}
log_events : {'parentResourceId': 'server-0987', 'idps_message': 'Failed to connect to DB', 'level': 'error', 'resourceId': 'server-1234675', 'traceId': 'abc-xyz-123', 'timestamp': '2023-12-16T08:00:00', 'spanId': 'span-456', 'commit': '5e5342f'}
log_events : {'parentResourceId': 'server-0987', 'idps_message': 'Server Error', 'level': 'error', 'resourceId': 'server-1234675', 'traceId': 'abc-xyz-32334', 'timestamp': '2023-12-16T08:00:00', 'spanId': 'span-456', 'commit': '5e5342f'}
~/dev-projects/november-2023-hiring-muskan399 $ python3 managment/command_line_cli.py

=============================================================
Hello! Use this CLI to filter,search,sort and groupby
=============================================================

Enter start time (e.g., 2020-02-01T00:00:00) [Default: 2020-02-01T00:00:00]: 2021-01-01T00:00:00                                                   
Enter end time (e.g., 2020-02-05T00:00:00) [Default: 2024-02-05T00:00:00]: 2024-01-01T00:00:00
Enter group_by (e.g., level) [Press Enter to skip]: 
Enter fields (e.g., message,level) [Default: message,level,resourceId,traceId,spanId,commit,parentResourceId,timestamp]: 
Enter sort (e.g., timestamp) [Default: timestamp]:          
Enter page[limit] [Default: 10]: 
Enter the project id [Default: 1]: 

Enter filter name (or press Enter to finish):
Allowed filters are:
1. level(equals,not equals, contains, not contains)
2. message(equals, not equals, contains, not contains)
3. resourceId(equals, not equals)
4. traceId(equals, not equals)
5. spanId(equals, not equals)
6. commit(equals, not equals)
7. parentResourceId(equals, not equals)
level
Enter filter type (EQUALS, NOT EQUALS, CONTAINS, NOT CONTAINS): error
Invalid filter type. Please enter a valid filter type.
Enter filter type (EQUALS, NOT EQUALS, CONTAINS, NOT CONTAINS): equals
Enter filter value for level [EQUALS]: error

Enter filter name (or press Enter to finish):
Allowed filters are:
1. level(equals,not equals, contains, not contains)
2. message(equals, not equals, contains, not contains)
3. resourceId(equals, not equals)
4. traceId(equals, not equals)
5. spanId(equals, not equals)
6. commit(equals, not equals)
7. parentResourceId(equals, not equals)
message
Enter filter type (EQUALS, NOT EQUALS, CONTAINS, NOT CONTAINS): contains
Enter filter value for message [CONTAINS]: ser

Enter filter name (or press Enter to finish):
Allowed filters are:
1. level(equals,not equals, contains, not contains)
2. message(equals, not equals, contains, not contains)
3. resourceId(equals, not equals)
4. traceId(equals, not equals)
5. spanId(equals, not equals)
6. commit(equals, not equals)
7. parentResourceId(equals, not equals)

API call successful(Note: Records are paginated)
log_events : {'parentResourceId': 'server-0987', 'idps_message': 'Server Error', 'level': 'error', 'resourceId': 'server-1234675', 'traceId': 'abc-qddyz-32334', 'timestamp': '2022-12-16T08:00:00', 'spanId': 'span-456', 'commit': '5e5342f'}
log_events : {'parentResourceId': 'server-0987', 'idps_message': 'Server Error', 'level': 'error', 'resourceId': 'server-1234675', 'traceId': 'abc-xyz-32334', 'timestamp': '2023-12-16T08:00:00', 'spanId': 'span-456', 'commit': '5e5342f'}
 ```
  
</details>
<details>
  <summary>With Groupby: groupby=level</summary>
  
 ```
=============================================================
Hello! Use this CLI to filter,search,sort and groupby
=============================================================

Enter start time (e.g., 2020-02-01T00:00:00) [Default: 2020-02-01T00:00:00]: 
Enter end time (e.g., 2020-02-05T00:00:00) [Default: 2024-02-05T00:00:00]: 
Enter group_by (e.g., level) [Press Enter to skip]: level
Enter sort (e.g., count) [Default: count(with groupby)]: 
Enter page[limit] [Default: 10]: 
Enter the project id [Default: 1]: 

Enter filter name (or press Enter to finish):
Allowed filters are:
1. level(equals,not equals, contains, not contains)
2. message(equals, not equals, contains, not contains)
3. resourceId(equals, not equals)
4. traceId(equals, not equals)
5. spanId(equals, not equals)
6. commit(equals, not equals)
7. parentResourceId(equals, not equals)

API call successful(Note: Records are paginated)
log_events : {'level': 'info', 'count': 3}
log_events : {'level': 'error', 'count': 3}


 ```
  
</details>
Similarly we have other combinations for filter+groupby, multi-filters, sort and between timerange.


<!-- ROADMAP -->
## Improvements

- [ ] Instead of this CLI, UI would have been a better option with all the timerange, groupby and filter type dropdown options.
- [ ] Addition of Unittests.
- [ ] Instead of RDS, databases like Redshift would have been better.


<!-- CONTRIBUTING -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->

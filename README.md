# athena_regulation

## Architecture
![](img/2024-01-26-10-19-23.png)

## Lambda Code
src/lambda_code.py
- python3.10
- Change any of the following as needed (s3_bucket name must be changed)
    ```
    region_name = 'ap-northeast-2'
    s3_bucket = 'chiholee-athena-regulation'
    ```

## Table
### athena_cloudtrail_info
| Column Name | Type | PK | Description |
| -------- | -------- | -------- | -------- |
| event_id | string | V | ... |
| query_execution_id | string |  | ... |
| request_id | string |  | ... |
| event_name | string |  | ... |
| type | string |  | ... |
| principal_id | string |  | ... |
| arn | string |  | ... |
| account_id | string |  | ... |
| access_key_id | string |  | ... |
| user_name | string |  | ... |
| event_source | string |  | ... |
| source_ip_address | string |  | ... |


### athena_sql_info
| Column Name | Type | PK  | Description |
| ----------- | ---- | --- | ----------- |
| query_execution_id | string | V | ...|
| catalog | string | | ...|
| database | string | | ...|
| statement_type | string | | ...|
| result_configuration | string | | ...|
| submission_datetime | string | | ...|
| completion_datetime | string | | ...|
| state | string | | ...|
| substatement_type | string | | ...|
| workgroup | string | | ...|
| query | string | | ...|


## Athena Audit Query
```sql
select *
from athena_cloudtrail_info a,
     athena_sql_info b
where a.query_execution_id = b.query_execution_id;
```

## QuickSight
...
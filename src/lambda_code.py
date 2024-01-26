import boto3
import json
from datetime import datetime, timedelta

def get_utc_time(minutes):
    utc_now = datetime.utcnow()
    utc_time = utc_now - timedelta(minutes=minutes)    
    return utc_time

def save_cloudtrail_events(cloudtrail_client, s3_client, s3_bucket, event_source, utc_start_time, utc_end_time):
    response = cloudtrail_client.lookup_events(
        LookupAttributes=[
            {
                'AttributeKey': 'EventSource',
                'AttributeValue': event_source,
            },
        ],
        StartTime=utc_start_time,
        EndTime=utc_end_time,
    )

    query_execution_ids = []

    print("# Save CloudTrail")
    for event in response['Events']:
        event_name = event['EventName']

        if event_name == "StartQueryExecution":
            event_str = event['CloudTrailEvent']
            event_dict = json.loads(event_str)

            json_data = {
                'event_id': event_dict['eventID'],
                'query_execution_id': event_dict['responseElements']['queryExecutionId'],
                'request_id': event_dict['requestID'],
                'event_name': event_dict['eventName'],
                'type': event_dict['userIdentity']['type'],
                'principal_id': event_dict['userIdentity']['principalId'],
                'arn': event_dict['userIdentity']['arn'],
                'account_id': event_dict['userIdentity']['accountId'],
                'access_key_id': event_dict['userIdentity']['accessKeyId'],
                'user_name': event_dict['userIdentity']['userName'],
                'event_source': event_dict['eventSource'],
                'source_ip_address': event_dict['sourceIPAddress']
            }

            json_string = json.dumps(json_data, default=str)

            event_id = event_dict['eventID']
            query_execution_id = event_dict['responseElements']['queryExecutionId']

            query_execution_ids.append(query_execution_id)

            s3_key = f'athena_cloudtrail_info/{event_id}.json'

            s3_client.put_object(Bucket=s3_bucket, Key=s3_key, Body=json_string)

            print(f'JSON data saved to S3: s3://{s3_bucket}/{s3_key}')

    return query_execution_ids

def save_query_info(athena_client, s3_client, s3_bucket, query_execution_ids):
    print("# Save Query")
    query_execution_ids = list(set(query_execution_ids))

    for query_execution_id in query_execution_ids:
        query_execution_response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)

        json_data = {
            'query_execution_id': query_execution_response['QueryExecution']['QueryExecutionId'],
            'catalog': query_execution_response['QueryExecution']['QueryExecutionContext']['Catalog'],
            'database': query_execution_response['QueryExecution']['QueryExecutionContext']['Database'],
            'statement_type': query_execution_response['QueryExecution']['StatementType'],
            'result_configuration': query_execution_response['QueryExecution']['ResultConfiguration']['OutputLocation'],
            'submission_datetime': query_execution_response['QueryExecution']['Status']['SubmissionDateTime'],
            'completion_datetime': query_execution_response['QueryExecution']['Status']['CompletionDateTime'],
            'state': query_execution_response['QueryExecution']['Status']['State'],
            'substatement_type': query_execution_response['QueryExecution']['SubstatementType'],
            'workgroup': query_execution_response['QueryExecution']['WorkGroup'],
            'query': query_execution_response['QueryExecution']['Query']
        }

        json_string = json.dumps(json_data, default=str)

        s3_key = f'athena_sql_info/{query_execution_id}.json'

        s3_client.put_object(Bucket=s3_bucket, Key=s3_key, Body=json_string)

        print(f'JSON data saved to S3: s3://{s3_bucket}/{s3_key}')

def lambda_handler(event, context):
    
    region_name = 'ap-northeast-2'
    s3_bucket = 'chiholee-athena-regulation'
    event_source = 'athena.amazonaws.com'
    athena_client = boto3.client('athena', region_name=region_name)
    s3_client = boto3.client('s3', region_name=region_name)
    cloudtrail_client = boto3.client('cloudtrail', region_name=region_name)

    utc_start_time = get_utc_time(70) 
    utc_end_time = datetime.utcnow()

    query_execution_ids = save_cloudtrail_events(cloudtrail_client, s3_client, s3_bucket, event_source, utc_start_time, utc_end_time)
    save_query_info(athena_client, s3_client, s3_bucket, query_execution_ids)
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Finish!')
    }

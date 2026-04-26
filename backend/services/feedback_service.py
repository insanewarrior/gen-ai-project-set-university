from datetime import datetime, timezone

import boto3

import config


def _get_table():
    kwargs = {'region_name': 'us-east-1'}
    if config.DYNAMODB_ENDPOINT:
        kwargs['endpoint_url'] = config.DYNAMODB_ENDPOINT
        kwargs['aws_access_key_id'] = 'fake'
        kwargs['aws_secret_access_key'] = 'fake'
    dynamodb = boto3.resource('dynamodb', **kwargs)
    return dynamodb.Table(config.FEEDBACK_TABLE_NAME)


def submit_feedback(query_id: str, user_id: str, rating: str) -> None:
    _get_table().put_item(Item={
        'queryId': query_id,
        'userId': user_id,
        'rating': rating,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    })

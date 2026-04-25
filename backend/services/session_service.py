import uuid
from datetime import datetime
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

import config


def _to_decimal(obj):
    """Recursively convert floats to Decimal for DynamoDB compatibility."""
    if isinstance(obj, list):
        return [_to_decimal(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, float):
        return Decimal(str(obj))
    return obj


def _get_table():
    kwargs = {'region_name': 'us-east-1'}
    if config.DYNAMODB_ENDPOINT:
        kwargs['endpoint_url'] = config.DYNAMODB_ENDPOINT
        kwargs['aws_access_key_id'] = 'fake'
        kwargs['aws_secret_access_key'] = 'fake'
    dynamodb = boto3.resource('dynamodb', **kwargs)
    return dynamodb.Table(config.SESSIONS_TABLE_NAME)


def create_session(user_id: str, data: dict) -> dict:
    session_id = str(uuid.uuid4())
    session_date = data['sessionDate']
    sk = f"{session_date}#{session_id}"
    created_at = datetime.utcnow().isoformat() + 'Z'
    item = {
        'userId': user_id,
        'sk': sk,
        'sessionId': session_id,
        'sessionDate': session_date,
        'sport': data['sport'],
        'exercises': _to_decimal(data['exercises']),
        'createdAt': created_at,
    }
    if data.get('notes'):
        item['notes'] = data['notes']
    _get_table().put_item(Item=item)
    return item


def get_sessions(user_id: str) -> list:
    response = _get_table().query(
        KeyConditionExpression=Key('userId').eq(user_id),
        ScanIndexForward=False,  # newest first
    )
    return response['Items']


def get_session(
    user_id: str, session_id: str, session_date: str
) -> dict | None:
    sk = f"{session_date}#{session_id}"
    response = _get_table().get_item(Key={'userId': user_id, 'sk': sk})
    return response.get('Item')


def get_month_count(user_id: str, year_month: str) -> int:
    response = _get_table().query(
        KeyConditionExpression=(
            Key('userId').eq(user_id) & Key('sk').begins_with(year_month)
        ),
        Select='COUNT',
    )
    return response['Count']

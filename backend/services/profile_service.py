from datetime import datetime, timedelta

import boto3
from boto3.dynamodb.conditions import Key

import config
import services.rate_limit_service as rate_limit_service


def _get_sessions_table():
    kwargs = {'region_name': 'us-east-1'}
    if config.DYNAMODB_ENDPOINT:
        kwargs['endpoint_url'] = config.DYNAMODB_ENDPOINT
        kwargs['aws_access_key_id'] = 'fake'
        kwargs['aws_secret_access_key'] = 'fake'
    dynamodb = boto3.resource('dynamodb', **kwargs)
    return dynamodb.Table(config.SESSIONS_TABLE_NAME)


def _get_usage_table():
    kwargs = {'region_name': 'us-east-1'}
    if config.DYNAMODB_ENDPOINT:
        kwargs['endpoint_url'] = config.DYNAMODB_ENDPOINT
        kwargs['aws_access_key_id'] = 'fake'
        kwargs['aws_secret_access_key'] = 'fake'
    dynamodb = boto3.resource('dynamodb', **kwargs)
    return dynamodb.Table(config.QUERY_USAGE_TABLE_NAME)


def get_total_session_count(user_id: str) -> int:
    response = _get_sessions_table().query(
        KeyConditionExpression=Key('userId').eq(user_id),
        Select='COUNT',
    )
    return response['Count']


def get_total_query_count(user_id: str) -> int:
    """Sum all daily queryCount entries (exclude burst: SK prefix items)."""
    response = _get_usage_table().query(
        KeyConditionExpression=Key('userId').eq(user_id),
    )
    total = 0
    for item in response.get('Items', []):
        sk = item.get('date', '')
        if not sk.startswith('burst:'):
            total += int(item.get('queryCount', 0))
    return total


_FREE_TIER = "free"
_ONBOARDING_TIER = "onboarding"
_PREMIUM_TIER = "premium"


def resolve_tier(user_create_date: str | None, is_premium: bool) -> str:
    if is_premium:
        return _PREMIUM_TIER
    if user_create_date:
        try:
            created = datetime.fromisoformat(user_create_date.replace("Z", ""))
            if (datetime.utcnow() - created).days < 7:
                return _ONBOARDING_TIER
        except (ValueError, AttributeError):
            pass
    return _FREE_TIER

from datetime import datetime, timedelta

import boto3
from botocore.exceptions import ClientError

import config

_FREE_TIER_LIMIT = 20
_ONBOARDING_LIMIT = 10
_ONBOARDING_DAYS = 7


def _get_table():
    kwargs = {'region_name': 'us-east-1'}
    if config.DYNAMODB_ENDPOINT:
        kwargs['endpoint_url'] = config.DYNAMODB_ENDPOINT
        kwargs['aws_access_key_id'] = 'fake'
        kwargs['aws_secret_access_key'] = 'fake'
    dynamodb = boto3.resource('dynamodb', **kwargs)
    return dynamodb.Table(config.QUERY_USAGE_TABLE_NAME)


def _next_midnight() -> str:
    return (datetime.utcnow().date() + timedelta(days=1)).isoformat() + "T00:00:00Z"


def check_and_increment(user_id: str, user_create_date: str | None = None) -> dict:
    table = _get_table()
    today = datetime.utcnow().strftime("%Y-%m-%d")

    tier_limit = _FREE_TIER_LIMIT
    if user_create_date:
        try:
            created = datetime.fromisoformat(user_create_date.replace("Z", ""))
            if (datetime.utcnow() - created).days < _ONBOARDING_DAYS:
                tier_limit = _ONBOARDING_LIMIT
        except (ValueError, AttributeError):
            pass

    try:
        response = table.update_item(
            Key={"userId": user_id, "date": today},
            UpdateExpression="SET queryCount = if_not_exists(queryCount, :zero) + :one",
            ConditionExpression="attribute_not_exists(queryCount) OR queryCount < :limit",
            ExpressionAttributeValues={":zero": 0, ":one": 1, ":limit": tier_limit},
            ReturnValues="UPDATED_NEW",
        )
        new_count = int(response["Attributes"]["queryCount"])
        return {
            "allowed": True,
            "queries_remaining": tier_limit - new_count,
            "tier_limit": tier_limit,
            "reset_at": _next_midnight(),
        }
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {"allowed": False, "queries_remaining": 0, "reset_at": _next_midnight()}
        raise

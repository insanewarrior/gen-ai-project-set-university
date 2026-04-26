from datetime import datetime, timedelta

import boto3
from botocore.exceptions import ClientError

import config

_FREE_TIER_LIMIT = 3
_ONBOARDING_LIMIT = 10
_ONBOARDING_DAYS = 7
_PREMIUM_BURST_LIMIT = 10  # queries per minute for premium users


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


def _next_minute() -> str:
    dt = datetime.utcnow().replace(second=0, microsecond=0) + timedelta(minutes=1)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _check_burst(user_id: str) -> dict:
    table = _get_table()
    minute_key = datetime.utcnow().strftime("%Y-%m-%dT%H:%M")
    try:
        response = table.update_item(
            Key={"userId": user_id, "date": f"burst:{minute_key}"},
            UpdateExpression="SET queryCount = if_not_exists(queryCount, :zero) + :one",
            ConditionExpression="attribute_not_exists(queryCount) OR queryCount < :limit",
            ExpressionAttributeValues={
                ":zero": 0, ":one": 1, ":limit": _PREMIUM_BURST_LIMIT
            },
            ReturnValues="UPDATED_NEW",
        )
        int(response["Attributes"]["queryCount"])
        return {
            "allowed": True,
            "queries_remaining": -1,
            "tier_limit": -1,
            "reset_at": _next_minute(),
        }
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {"allowed": False, "queries_remaining": 0, "tier_limit": -1, "reset_at": _next_minute()}
        raise


def get_today_count(user_id: str) -> int:
    table = _get_table()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    response = table.get_item(Key={"userId": user_id, "date": today})
    item = response.get("Item")
    if item is None:
        return 0
    return int(item.get("queryCount", 0))


def check_and_increment(
    user_id: str,
    user_create_date: str | None = None,
    is_premium: bool = False,
) -> dict:
    if is_premium:
        return _check_burst(user_id)

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
            return {"allowed": False, "queries_remaining": 0, "tier_limit": tier_limit, "reset_at": _next_midnight()}
        raise

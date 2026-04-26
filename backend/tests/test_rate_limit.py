"""Tests for rate_limit_service — uses moto DynamoDB mock."""
import os
from datetime import datetime

import boto3
import pytest
from moto import mock_aws

import config


@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["DYNAMODB_ENDPOINT"] = ""


@pytest.fixture
def dynamodb_table():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="QueryUsage",
            KeySchema=[
                {"AttributeName": "userId", "KeyType": "HASH"},
                {"AttributeName": "date", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "userId", "AttributeType": "S"},
                {"AttributeName": "date", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield


def _make_table():
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="QueryUsage",
        KeySchema=[
            {"AttributeName": "userId", "KeyType": "HASH"},
            {"AttributeName": "date", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "userId", "AttributeType": "S"},
            {"AttributeName": "date", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )


def test_first_query_allowed(monkeypatch):
    monkeypatch.setattr(config, "QUERY_USAGE_TABLE_NAME", "QueryUsage")
    monkeypatch.setattr(config, "DYNAMODB_ENDPOINT", "")
    import importlib
    import services.rate_limit_service as rate_limit_service
    importlib.reload(rate_limit_service)

    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="QueryUsage",
            KeySchema=[
                {"AttributeName": "userId", "KeyType": "HASH"},
                {"AttributeName": "date", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "userId", "AttributeType": "S"},
                {"AttributeName": "date", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        result = rate_limit_service.check_and_increment("user-001")
        assert result["allowed"] is True
        assert result["queries_remaining"] == 2  # limit 3 - 1 used


def test_limit_enforced_on_4th_free_tier(monkeypatch):
    monkeypatch.setattr(config, "QUERY_USAGE_TABLE_NAME", "QueryUsage")
    monkeypatch.setattr(config, "DYNAMODB_ENDPOINT", "")
    import importlib
    import services.rate_limit_service as rate_limit_service
    importlib.reload(rate_limit_service)

    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="QueryUsage",
            KeySchema=[
                {"AttributeName": "userId", "KeyType": "HASH"},
                {"AttributeName": "date", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "userId", "AttributeType": "S"},
                {"AttributeName": "date", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        for _ in range(3):
            r = rate_limit_service.check_and_increment("user-002")
            assert r["allowed"] is True

        fourth = rate_limit_service.check_and_increment("user-002")
        assert fourth["allowed"] is False
        assert fourth["queries_remaining"] == 0


def test_reset_at_is_tomorrow_midnight(monkeypatch):
    monkeypatch.setattr(config, "QUERY_USAGE_TABLE_NAME", "QueryUsage")
    monkeypatch.setattr(config, "DYNAMODB_ENDPOINT", "")
    import importlib
    import services.rate_limit_service as rate_limit_service
    importlib.reload(rate_limit_service)

    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="QueryUsage",
            KeySchema=[
                {"AttributeName": "userId", "KeyType": "HASH"},
                {"AttributeName": "date", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "userId", "AttributeType": "S"},
                {"AttributeName": "date", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        result = rate_limit_service.check_and_increment("user-003")
        reset_at = result["reset_at"]
        # Format: YYYY-MM-DDT00:00:00Z
        assert reset_at.endswith("T00:00:00Z")
        date_part = reset_at.replace("T00:00:00Z", "")
        parts = date_part.split("-")
        assert len(parts) == 3
        assert len(parts[0]) == 4  # year
        assert len(parts[1]) == 2  # month
        assert len(parts[2]) == 2  # day


def test_onboarding_tier_allows_10_queries(monkeypatch):
    monkeypatch.setattr(config, "QUERY_USAGE_TABLE_NAME", "QueryUsage")
    monkeypatch.setattr(config, "DYNAMODB_ENDPOINT", "")
    import importlib
    import services.rate_limit_service as rate_limit_service
    importlib.reload(rate_limit_service)

    today_iso = datetime.utcnow().isoformat()

    with mock_aws():
        _make_table()
        for i in range(10):
            r = rate_limit_service.check_and_increment(
                "user-onboard", user_create_date=today_iso
            )
            assert r["allowed"] is True, f"query {i+1} should be allowed"
            assert r["tier_limit"] == 10

        eleventh = rate_limit_service.check_and_increment(
            "user-onboard", user_create_date=today_iso
        )
        assert eleventh["allowed"] is False
        assert eleventh["queries_remaining"] == 0


def test_premium_user_skips_daily_limit(monkeypatch):
    """Premium users exceed free tier daily limit (3) — no daily cap enforced."""
    monkeypatch.setattr(config, "QUERY_USAGE_TABLE_NAME", "QueryUsage")
    monkeypatch.setattr(config, "DYNAMODB_ENDPOINT", "")
    import importlib
    import services.rate_limit_service as rate_limit_service
    importlib.reload(rate_limit_service)

    with mock_aws():
        _make_table()
        # Call 5 times — exceeds free-tier daily limit of 3, under burst limit of 10
        for i in range(5):
            r = rate_limit_service.check_and_increment(
                "user-premium-daily", is_premium=True
            )
            assert r["allowed"] is True, f"query {i+1} should be allowed"
            assert r["queries_remaining"] == -1


def test_premium_burst_limit_enforced(monkeypatch):
    monkeypatch.setattr(config, "QUERY_USAGE_TABLE_NAME", "QueryUsage")
    monkeypatch.setattr(config, "DYNAMODB_ENDPOINT", "")
    import importlib
    import services.rate_limit_service as rate_limit_service
    importlib.reload(rate_limit_service)

    with mock_aws():
        _make_table()
        for i in range(10):
            r = rate_limit_service.check_and_increment(
                "user-premium-burst", is_premium=True
            )
            assert r["allowed"] is True, f"query {i+1} should be allowed"

        eleventh = rate_limit_service.check_and_increment(
            "user-premium-burst", is_premium=True
        )
        assert eleventh["allowed"] is False
        assert eleventh["queries_remaining"] == 0


def test_user_create_date_none_defaults_to_free_tier(monkeypatch):
    monkeypatch.setattr(config, "QUERY_USAGE_TABLE_NAME", "QueryUsage")
    monkeypatch.setattr(config, "DYNAMODB_ENDPOINT", "")
    import importlib
    import services.rate_limit_service as rate_limit_service
    importlib.reload(rate_limit_service)

    with mock_aws():
        _make_table()
        r = rate_limit_service.check_and_increment(
            "user-no-date", user_create_date=None
        )
        assert r["allowed"] is True
        assert r["tier_limit"] == rate_limit_service._FREE_TIER_LIMIT
        assert r["tier_limit"] == 3

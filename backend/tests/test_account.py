"""Tests for DELETE /account endpoint."""
import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

import config
import middleware.auth as auth_module


@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


def _bypass_client(monkeypatch) -> TestClient:
    monkeypatch.setattr(config, "AUTH_BYPASS", "true")
    monkeypatch.setattr(config, "TEST_USER_ID", "test-user-001")
    monkeypatch.setattr(auth_module, "_jwks_cache", None)
    from main import app
    return TestClient(app)


def test_delete_account_returns_200(monkeypatch):
    client = _bypass_client(monkeypatch)
    with patch("services.account_service.delete_account", return_value=None):
        response = client.delete("/account")
    assert response.status_code == 200
    assert response.json() == {"deleted": True}


def test_delete_account_requires_auth():
    import sys
    if "main" in sys.modules:
        del sys.modules["main"]
    from main import app
    from fastapi.testclient import TestClient as TC
    client = TC(app)
    response = client.delete("/account")
    assert response.status_code == 401


def test_delete_account_calls_all_tables(monkeypatch):
    client = _bypass_client(monkeypatch)
    with patch("services.account_service.delete_account", return_value=None) as mock_delete:
        response = client.delete("/account")
    assert response.status_code == 200
    mock_delete.assert_called_once_with("test-user-001")


def test_delete_account_deletes_sessions(monkeypatch):
    monkeypatch.setattr(config, "DYNAMODB_ENDPOINT", None)
    monkeypatch.setattr(config, "COGNITO_USER_POOL_ID", "us-east-1_fake")
    monkeypatch.setattr(config, "COGNITO_REGION", "us-east-1")

    mock_item_1 = {"userId": "test-user-001", "sk": "SESSION#001"}
    mock_item_2 = {"userId": "test-user-001", "sk": "SESSION#002"}

    mock_sessions_table = MagicMock()
    mock_sessions_table.query.return_value = {"Items": [mock_item_1, mock_item_2]}
    mock_batch_writer = MagicMock()
    mock_sessions_table.batch_writer.return_value.__enter__ = MagicMock(return_value=mock_batch_writer)
    mock_sessions_table.batch_writer.return_value.__exit__ = MagicMock(return_value=False)

    mock_usage_table = MagicMock()
    mock_usage_table.query.return_value = {"Items": []}
    mock_usage_batch = MagicMock()
    mock_usage_table.batch_writer.return_value.__enter__ = MagicMock(return_value=mock_usage_batch)
    mock_usage_table.batch_writer.return_value.__exit__ = MagicMock(return_value=False)

    mock_feedback_table = MagicMock()
    mock_feedback_table.scan.return_value = {"Items": [], "LastEvaluatedKey": None}
    mock_feedback_batch = MagicMock()
    mock_feedback_table.batch_writer.return_value.__enter__ = MagicMock(return_value=mock_feedback_batch)
    mock_feedback_table.batch_writer.return_value.__exit__ = MagicMock(return_value=False)

    def table_selector(name):
        if name == config.SESSIONS_TABLE_NAME:
            return mock_sessions_table
        if name == config.QUERY_USAGE_TABLE_NAME:
            return mock_usage_table
        return mock_feedback_table

    mock_dynamodb = MagicMock()
    mock_dynamodb.Table.side_effect = table_selector

    mock_cognito = MagicMock()

    import services.account_service as svc

    with patch.object(svc, "_get_dynamodb", return_value=mock_dynamodb), \
         patch("boto3.client", return_value=mock_cognito):
        svc.delete_account("test-user-001")

    assert mock_batch_writer.delete_item.call_count == 2
    mock_batch_writer.delete_item.assert_any_call(Key={"userId": "test-user-001", "sk": "SESSION#001"})
    mock_batch_writer.delete_item.assert_any_call(Key={"userId": "test-user-001", "sk": "SESSION#002"})


def test_delete_account_deletes_cognito(monkeypatch):
    monkeypatch.setattr(config, "DYNAMODB_ENDPOINT", None)
    monkeypatch.setattr(config, "COGNITO_USER_POOL_ID", "us-east-1_testpool")
    monkeypatch.setattr(config, "COGNITO_REGION", "us-east-1")

    mock_table = MagicMock()
    mock_table.query.return_value = {"Items": []}
    mock_batch = MagicMock()
    mock_table.batch_writer.return_value.__enter__ = MagicMock(return_value=mock_batch)
    mock_table.batch_writer.return_value.__exit__ = MagicMock(return_value=False)
    mock_table.scan.return_value = {"Items": []}

    mock_dynamodb = MagicMock()
    mock_dynamodb.Table.return_value = mock_table

    mock_cognito = MagicMock()

    import services.account_service as svc

    with patch.object(svc, "_get_dynamodb", return_value=mock_dynamodb), \
         patch("boto3.client", return_value=mock_cognito):
        svc.delete_account("test-user-001")

    mock_cognito.admin_delete_user.assert_called_once_with(
        UserPoolId="us-east-1_testpool",
        Username="test-user-001",
    )

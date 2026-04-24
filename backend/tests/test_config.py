import importlib
import os


def test_config_defaults():
    import config

    importlib.reload(config)
    assert config.SESSIONS_TABLE_NAME == "Sessions"
    assert config.QUERY_USAGE_TABLE_NAME == "QueryUsage"
    assert config.FEEDBACK_TABLE_NAME == "Feedback"
    assert config.S3_FAISS_BUCKET is None


def test_config_from_env(monkeypatch):
    monkeypatch.setenv("SESSIONS_TABLE_NAME", "MySessions")
    monkeypatch.setenv("QUERY_USAGE_TABLE_NAME", "MyUsage")
    monkeypatch.setenv("FEEDBACK_TABLE_NAME", "MyFeedback")
    monkeypatch.setenv("S3_FAISS_BUCKET", "my-bucket")

    import config

    importlib.reload(config)
    assert config.SESSIONS_TABLE_NAME == "MySessions"
    assert config.QUERY_USAGE_TABLE_NAME == "MyUsage"
    assert config.FEEDBACK_TABLE_NAME == "MyFeedback"
    assert config.S3_FAISS_BUCKET == "my-bucket"

import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from app.infrastructure.bigquery.bigquery_helper import BigQueryHelper

# Patch settings and Google modules globally for all tests
@pytest.fixture(autouse=True)
def patch_settings_and_google(monkeypatch):
    # Patch settings.gcp_key_file and settings.gcp_project_id
    class DummySettings:
        gcp_key_file = "dummy_key.json"
        gcp_project_id = "dummy_project"
    monkeypatch.setattr("app.core.config.settings", DummySettings())
    # Patch service_account and bigquery
    monkeypatch.setattr("app.infrastructure.bigquery.bigquery_helper.service_account.Credentials.from_service_account_info", lambda info, scopes=None: MagicMock())
    monkeypatch.setattr("app.infrastructure.bigquery.bigquery_helper.bigquery.Client", lambda credentials, project: MagicMock())
    yield

def test_setup_credentials_success(tmp_path, monkeypatch):
    # Create a dummy key file
    from unittest.mock import mock_open, patch
    from pathlib import Path
    key_data = {
        "type": "service_account",
        "project_id": "dummy_project",
        "private_key": "dummy_key",
        "client_email": "dummy@dummy.com"
    }
    key_file = tmp_path / "dummy_key.json"
    key_file.write_text(json.dumps(key_data))
    monkeypatch.setattr("app.core.config.settings.gcp_key_file", str(key_file), raising=False)
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(Path, "is_file", lambda self: True)
    m = mock_open(read_data=json.dumps(key_data))
    with patch("builtins.open", m):
        helper = BigQueryHelper()
    assert helper.credentials is not None

def test_setup_credentials_missing_file(monkeypatch):
    monkeypatch.setattr("app.core.config.settings.gcp_key_file", "nonexistent.json")
    with pytest.raises(FileNotFoundError):
        BigQueryHelper()

def test_setup_credentials_invalid_json(tmp_path, monkeypatch):
    from unittest.mock import mock_open, patch
    from pathlib import Path
    key_file = tmp_path / "invalid.json"
    key_file.write_text("not a json")
    monkeypatch.setattr("app.core.config.settings.gcp_key_file", str(key_file), raising=False)
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(Path, "is_file", lambda self: True)
    m = mock_open(read_data="not a json")
    with patch("builtins.open", m):
        with pytest.raises(ValueError):
            BigQueryHelper()

def test_validate_credentials_structure_missing_fields(monkeypatch):
    helper = BigQueryHelper.__new__(BigQueryHelper)
    helper.log_error = MagicMock()
    with pytest.raises(ValueError):
        helper._validate_credentials_structure({"type": "service_account"})

def test_setup_bigquery_client_no_credentials(monkeypatch):
    helper = BigQueryHelper.__new__(BigQueryHelper)
    helper.credentials = None
    helper.log_error = MagicMock()
    with pytest.raises(Exception):
        helper._setup_bigquery_client()

def test_execute_query_success(monkeypatch):
    helper = BigQueryHelper.__new__(BigQueryHelper)
    helper.client = MagicMock()
    query_job = MagicMock()
    query_job.result.return_value = [1, 2, 3]
    helper.client.query.return_value = query_job
    helper.log_debug = MagicMock()
    helper.log_info = MagicMock()
    results = helper.execute_query("SELECT 1")
    assert results == [1, 2, 3]

def test_get_query_job_info_success(monkeypatch):
    helper = BigQueryHelper.__new__(BigQueryHelper)
    helper.client = MagicMock()
    job = MagicMock(job_id="id", state="DONE", created=1, started=2, ended=3, total_bytes_processed=100, total_rows=10)
    helper.client.get_job.return_value = job
    info = helper.get_query_job_info("id")
    assert info["job_id"] == "id"
    assert info["state"] == "DONE"

def test_get_query_job_info_exception(monkeypatch):
    helper = BigQueryHelper.__new__(BigQueryHelper)
    helper.client = MagicMock()
    helper.client.get_job.side_effect = Exception("fail")
    helper.log_warning = MagicMock()
    info = helper.get_query_job_info("id")
    assert info is None

def test_validate_connection_success(monkeypatch):
    helper = BigQueryHelper.__new__(BigQueryHelper)
    helper.client = True
    helper.execute_query = MagicMock(return_value=[1])
    helper.log_info = MagicMock()
    assert helper.validate_connection() is True

def test_validate_connection_fail(monkeypatch):
    helper = BigQueryHelper.__new__(BigQueryHelper)
    helper.client = True
    helper.execute_query = MagicMock(return_value=[])
    helper.log_warning = MagicMock()
    assert helper.validate_connection() is False

def test_validate_connection_exception(monkeypatch):
    helper = BigQueryHelper.__new__(BigQueryHelper)
    helper.client = True
    helper.execute_query = MagicMock(side_effect=Exception("fail"))
    helper.log_error = MagicMock()
    assert helper.validate_connection() is False

def test_get_project_info_success(monkeypatch):
    helper = BigQueryHelper.__new__(BigQueryHelper)
    client = MagicMock()
    client.project = "pid"
    client.list_datasets.return_value = [1, 2]
    client.location = "us"
    helper.client = client
    info = helper.get_project_info()
    assert info["project_id"] == "pid"
    assert info["dataset_count"] == 2
    assert info["location"] == "us"

def test_get_project_info_no_client(monkeypatch):
    helper = BigQueryHelper.__new__(BigQueryHelper)
    helper.client = None
    helper.log_error = MagicMock()
    assert helper.get_project_info() == {}

def test_get_project_info_exception(monkeypatch):
    helper = BigQueryHelper.__new__(BigQueryHelper)
    client = MagicMock()
    client.project = "pid"
    client.list_datasets.side_effect = Exception("fail")
    helper.client = client
    helper.log_error = MagicMock()
    assert helper.get_project_info() == {}

def test_close_success(monkeypatch):
    helper = BigQueryHelper.__new__(BigQueryHelper)
    client = MagicMock()
    helper.client = client
    helper.log_info = MagicMock()
    helper.close()
    assert helper.client is None

def test_close_exception(monkeypatch):
    helper = BigQueryHelper.__new__(BigQueryHelper)
    client = MagicMock()
    client.close.side_effect = Exception("fail")
    helper.client = client
    helper.log_warning = MagicMock()
    helper.close()
    # The client is only set to None if no exception occurs, so here it should remain set
    assert helper.client is client

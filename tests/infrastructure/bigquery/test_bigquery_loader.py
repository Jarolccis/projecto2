import pytest
from unittest.mock import MagicMock, patch, mock_open
from app.infrastructure.bigquery.bigquery_loader import BigQueryLoader
from pathlib import Path

@pytest.fixture
def loader(tmp_path):
    # Crea un directorio temporal para queries
    queries_dir = tmp_path / "querys"
    queries_dir.mkdir()
    return BigQueryLoader(str(queries_dir))

def test_load_query_success(loader, tmp_path):
    # Crea un archivo SQL de prueba
    query_file = Path(loader.queries_dir) / "test_query.sql"
    query_file.write_text("SELECT * FROM table WHERE id = {id}")
    result = loader.load_query("test_query", id=123)
    assert result == "SELECT * FROM table WHERE id = 123"

def test_load_query_file_not_found(loader):
    with pytest.raises(FileNotFoundError):
        loader.load_query("no_existe")

def test_load_query_param_replacement(loader, tmp_path):
    query_file = Path(loader.queries_dir) / "param_query.sql"
    query_file.write_text("SELECT {campo} FROM {tabla} WHERE x = {valor}")
    result = loader.load_query("param_query", campo="id", tabla="users", valor=5)
    assert result == "SELECT id FROM users WHERE x = 5"

def test_load_query_unexpected_error(loader, tmp_path):
    # Archivo con parámetro faltante
    query_file = Path(loader.queries_dir) / "bad_query.sql"
    query_file.write_text("SELECT * FROM table WHERE id = {id}")
    with pytest.raises(KeyError):
        loader.load_query("bad_query")

def test_get_available_queries(loader, tmp_path):
    # Crea varios archivos SQL
    (Path(loader.queries_dir) / "a.sql").write_text("A")
    (Path(loader.queries_dir) / "b.sql").write_text("B")
    (Path(loader.queries_dir) / "c.sql").write_text("C")
    queries = loader.get_available_queries()
    assert set(queries) == {"a", "b", "c"}

def test_get_available_queries_no_dir(tmp_path):
    # Directorio no existe
    loader = BigQueryLoader(str(tmp_path / "no_dir"))
    queries = loader.get_available_queries()
    assert queries == []

def test_get_available_queries_exception(monkeypatch):
    loader = BigQueryLoader("/fake/path")
    # Fuerza una excepción en glob
    monkeypatch.setattr(Path, "glob", lambda self, pat: (_ for _ in ()).throw(Exception("fail")))
    queries = loader.get_available_queries()
    assert queries == []

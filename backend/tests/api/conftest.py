"""Cada prueba usa su propia base de datos temporal, sembrada desde cero."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    monkeypatch.setenv("SMART_HOME_DB", str(tmp_path / "prueba.sqlite"))
    from app.main import app

    with TestClient(app) as cliente_http:
        yield cliente_http

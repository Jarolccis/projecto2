import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.interfaces.api.controllers import healthy_controller

app = FastAPI()
app.include_router(healthy_controller.router)

client = TestClient(app)

def test_check_healthy():
    response = client.get("/status/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

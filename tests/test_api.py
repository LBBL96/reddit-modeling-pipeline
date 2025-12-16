import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data


def test_predict_endpoint():
    response = client.post(
        "/predict",
        json={"text": "This is a great product!"}
    )
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "sentiment" in data
        assert "confidence" in data
        assert data["sentiment"] in ["positive", "negative", "neutral"]


def test_predict_endpoint_empty_text():
    response = client.post(
        "/predict",
        json={"text": ""}
    )
    assert response.status_code == 422


def test_batch_predict_endpoint():
    response = client.post(
        "/predict/batch",
        json={"texts": ["Great!", "Terrible!", "Okay"]}
    )
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3


def test_model_info():
    response = client.get("/model/info")
    assert response.status_code == 200
    data = response.json()
    assert "deployed_model" in data
    assert "recent_models" in data

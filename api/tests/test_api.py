import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_predict_endpoint_from_json():
    with open("tests/json_test.json", encoding="utf-8") as f:
        payload = json.load(f)

    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    results = response.json()["predictions"]
    assert isinstance(results, list)
    for result in results:
        assert "predicted_affluence" in result
        assert "shap_values" in result
        assert isinstance(result["predicted_affluence"], float)
        assert isinstance(result["shap_values"], str)

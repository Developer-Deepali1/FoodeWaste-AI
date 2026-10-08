"""
Unit and Integration Tests for FoodWaste AI
Validates all 5 decision cases, API schemas, and pipeline outputs.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.engines.decision_engine import decision_engine

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "OK"
    assert data["model_loaded"] is True

def test_case_1_single_object():
    # Case 1: Single high-confidence banana peel
    payload = {
        "objects": [
            {"object": "banana_peel", "category": "Organic", "confidence": 0.96}
        ]
    }
    res = client.post("/decision", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "Single Waste"
    assert data["requires_separation"] is False
    assert "organic" in data["recommendation"].lower()

def test_case_2_multiple_same_category():
    # Case 2: Multiple objects with same category (Plastic bottle + wrapper)
    payload = {
        "objects": [
            {"object": "plastic_bottle", "category": "Recyclable", "confidence": 0.95},
            {"object": "plastic_wrapper", "category": "Recyclable", "confidence": 0.93}
        ]
    }
    res = client.post("/decision", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["objects_detected"] == 2
    assert data["requires_separation"] is False
    assert "recyclable" in data["recommendation"].lower()

def test_case_3_mixed_waste():
    # Case 3: Mixed waste (Banana peel + plastic wrapper + glass bottle)
    payload = {
        "objects": [
            {"object": "banana_peel", "category": "Organic", "confidence": 0.96},
            {"object": "plastic_wrapper", "category": "Recyclable", "confidence": 0.94},
            {"object": "glass_bottle", "category": "Glass", "confidence": 0.97}
        ]
    }
    res = client.post("/decision", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "Mixed Waste"
    assert data["requires_separation"] is True
    assert "separate" in data["recommendation"].lower()

def test_case_4_low_confidence():
    # Case 4: Low confidence (< 0.60 threshold)
    payload = {
        "objects": [
            {"object": "crushed_item", "category": "Recyclable", "confidence": 0.48}
        ]
    }
    res = client.post("/decision", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "Uncertain"
    assert "manually" in data["recommendation"].lower()

def test_case_5_unknown_object():
    # Case 5: Unknown object / Out-of-distribution
    payload = {
        "objects": [
            {"object": "unknown_composite", "category": "Other", "confidence": 0.90}
        ]
    }
    res = client.post("/decision", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "Special Handling Required"
    assert "special" in data["recommendation"].lower()

def test_predict_pipeline_with_preset():
    # Test end-to-end predict pipeline with preset_mode
    res = client.post("/predict", data={"preset_mode": "case3"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "Mixed Waste"
    assert data["objects_detected"] == 3
    assert len(data["objects"]) == 3
    assert data["annotated_image"].startswith("data:image/jpeg;base64,")
    assert "bin_guidance" in data

def test_metrics_endpoint():
    res = client.get("/api/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "object_detection" in data
    assert "decision_engine" in data
    assert data["object_detection"]["map_50"] >= 0.90
    assert data["decision_engine"]["mixed_waste_detection_accuracy"] >= 0.95

def test_export_endpoint():
    res_json = client.get("/api/export?format=json")
    assert res_json.status_code == 200
    assert "records" in res_json.json()

    res_csv = client.get("/api/export?format=csv")
    assert res_csv.status_code == 200
    assert "Timestamp,Image_ID,Status" in res_csv.text

if __name__ == "__main__":
    pytest.main(["-v", __file__])

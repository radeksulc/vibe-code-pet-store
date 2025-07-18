import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ensure backend is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))
from main import app

client = TestClient(app)

def test_list_pets():
    resp = client.get("/pets")
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data and isinstance(data["total"], int)
    assert "items" in data and isinstance(data["items"], list)
    # Default limit is 10
    assert len(data["items"]) <= 10
    assert data["total"] >= len(data["items"])

def test_create_get_update_delete_pet():
    # Create
    new_pet = {"name": "Testy", "species": "Hamster", "age": 1}
    resp = client.post("/pets", json=new_pet)
    assert resp.status_code == 201
    pet = resp.json()
    assert pet["name"] == "Testy"
    pet_id = pet["id"]

    # Get
    resp = client.get(f"/pets/{pet_id}")
    assert resp.status_code == 200
    pet = resp.json()
    assert pet["name"] == "Testy"

    # Update
    updated = {"name": "Testy2", "species": "Hamster", "age": 2}
    resp = client.put(f"/pets/{pet_id}", json=updated)
    assert resp.status_code == 200
    pet = resp.json()
    assert pet["name"] == "Testy2"
    assert pet["age"] == 2

    # Delete
    resp = client.delete(f"/pets/{pet_id}")
    assert resp.status_code == 204

    # Confirm deletion
    resp = client.get(f"/pets/{pet_id}")
    assert resp.status_code == 404

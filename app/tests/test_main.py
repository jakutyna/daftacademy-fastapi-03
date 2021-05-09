import pytest

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


def test_categories(test_client):
    response = test_client.get('/categories')
    assert response.status_code == 200
    assert response.json() == {"categories": [
        {"id": 1, "name": "Beverages"},
        {"id": 2, "name": "Condiments"},
        {"id": 3, "name": "Confections"},
        {"id": 4, "name": "Dairy Products"},
        {"id": 5, "name": "Grains/Cereals"},
        {"id": 6, "name": "Meat/Poultry"},
        {"id": 7, "name": "Produce"},
        {"id": 8, "name": "Seafood"},
    ]}


def test_customers(test_client):
    response = test_client.get('/customers')
    assert response.status_code == 200
    example_customer = {
        "id": "ALFKI",
        "name": "Alfreds Futterkiste",
        "full_address": "Obere Str. 57 12209 Berlin Germany",
    }
    assert example_customer in response.json()["customers"]

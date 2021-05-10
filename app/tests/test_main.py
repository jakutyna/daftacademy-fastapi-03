import pytest

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


def test_categories(test_client):
    response = test_client.get("/categories")
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
    response = test_client.get("/customers")
    assert response.status_code == 200
    example_customer = {
        "id": "ALFKI",
        "name": "Alfreds Futterkiste",
        "full_address": "Obere Str. 57 12209 Berlin Germany",
    }
    assert example_customer in response.json()["customers"]


def test_product_id(test_client):
    response = test_client.get("/products/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Chai"}
    response = test_client.get("/products/1000")
    assert response.status_code == 404


def test_employees(test_client):
    example_employee = {"id": 1, "last_name": "Davolio", "first_name": "Nancy", "city": "Seattle"}
    response = test_client.get("/employees")
    assert response.status_code == 200
    assert example_employee in response.json()["employees"]
    response = test_client.get("/employees?order=foo")
    assert response.status_code == 400


def test_products_extended(test_client):
    response = test_client.get("/products_extended")
    assert response.status_code == 200
    example_product = {
        "id": 1,
        "name": "Chai",
        "category": "Beverages",
        "supplier": "Exotic Liquids",
    }
    assert example_product in response.json()["products_extended"]


def test_product_orders(test_client):
    response = test_client.get("/products/10/orders")
    assert response.status_code == 200
    example_order = {
            "id": 10273,
            "customer": "QUICK-Stop",
            "quantity": 24,
            "total_price": 565.44,
        }
    assert example_order in response.json()["orders"]
    response = test_client.get("/products/1000/order")
    assert response.status_code == 404


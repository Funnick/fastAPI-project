from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_id_validation():
    response = client.post(
        "/solution",
        headers={"Content-Type": "application/json"},
        json={
            "orders": [
                {
                    "id": 1,
                    "item": "Laptop",
                    "quantity": 1,
                    "price": 999.99,
                    "status": "completed",
                },
                {
                    "id": 1,
                    "item": "Laptop",
                    "quantity": 1,
                    "price": 999.99,
                    "status": "completed",
                },
            ],
            "criterion": "completed",
        },
    )

    assert response.status_code == 400
    assert response.json()["message"] == "There are two items with the same id"


def test_quantity_validation():
    response = client.post(
        "/solution",
        headers={"Content-Type": "application/json"},
        json={
            "orders": [
                {
                    "id": 1,
                    "item": "Laptop",
                    "quantity": -1,
                    "price": 999.99,
                    "status": "completed",
                },
            ],
            "criterion": "completed",
        },
    )

    assert response.status_code == 400
    assert response.json()["message"] == "There is an item with negative quantity"


def test_price_validation():
    response = client.post(
        "/solution",
        headers={"Content-Type": "application/json"},
        json={
            "orders": [
                {
                    "id": 1,
                    "item": "Laptop",
                    "quantity": 1,
                    "price": -999.99,
                    "status": "completed",
                },
            ],
            "criterion": "completed",
        },
    )

    assert response.status_code == 400
    assert response.json()["message"] == "There is an item with negative price"


def test_status_validation():
    response = client.post(
        "/solution",
        headers={"Content-Type": "application/json"},
        json={
            "orders": [
                {
                    "id": 1,
                    "item": "Laptop",
                    "quantity": 1,
                    "price": 999.99,
                    "status": "something else",
                },
            ],
            "criterion": "completed",
        },
    )

    assert response.status_code == 400
    assert response.json()["message"] == "There is an item with bad status"


def test_criterion_validation():
    response = client.post(
        "/solution",
        headers={"Content-Type": "application/json"},
        json={
            "orders": [
                {
                    "id": 1,
                    "item": "Laptop",
                    "quantity": 1,
                    "price": 999.99,
                    "status": "completed",
                },
            ],
            "criterion": "something else",
        },
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Bad criterion"

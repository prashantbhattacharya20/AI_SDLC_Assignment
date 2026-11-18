from fastapi.testclient import TestClient


def test_submit_expense_contract(client: TestClient):
    headers = {
        "X-User-Id": "11111111-1111-1111-1111-111111111111",
        "X-User-Role": "EMPLOYEE",
    }
    payload = {
        "amount": 750.50,
        "currency": "INR",
        "category": "Meals",
        "description": "Lunch meeting with product design team",
        "expense_date": "2026-11-18",
    }
    response = client.post("/api/v1/expenses", json=payload, headers=headers)
    assert response.status_code == 201

    data = response.json()
    # Contract schema assertions
    assert "id" in data
    assert data["employee_id"] == "11111111-1111-1111-1111-111111111111"
    assert float(data["amount"]) == 750.50
    assert data["currency"] == "INR"
    assert data["category"] == "Meals"
    assert data["description"] == "Lunch meeting with product design team"
    assert data["expense_date"] == "2026-11-18"
    assert data["status"] == "SUBMITTED"
    assert "created_at" in data
    assert "updated_at" in data

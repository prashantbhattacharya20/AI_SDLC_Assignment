from fastapi.testclient import TestClient


def _create_submitted_expense(client: TestClient) -> str:
    headers = {
        "X-User-Id": "11111111-1111-1111-1111-111111111111",
        "X-User-Role": "EMPLOYEE",
    }
    payload = {
        "amount": 1250.00,
        "currency": "INR",
        "category": "Travel",
        "description": "Client visit cab fare",
        "expense_date": "2026-11-18",
    }
    resp = client.post("/api/v1/expenses", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()["id"]


def test_approve_expense_contract(client: TestClient):
    expense_id = _create_submitted_expense(client)
    manager_headers = {
        "X-User-Id": "22222222-2222-2222-2222-222222222222",
        "X-User-Role": "MANAGER",
    }
    approve_payload = {"comments": "Approved for client travel"}

    response = client.post(
        f"/api/v1/expenses/{expense_id}/approve",
        json=approve_payload,
        headers=manager_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == expense_id
    assert data["status"] == "APPROVED"
    assert data["currency"] == "INR"
    assert "employee_id" in data
    assert "amount" in data
    assert "category" in data
    assert "description" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_reject_expense_contract(client: TestClient):
    expense_id = _create_submitted_expense(client)
    manager_headers = {
        "X-User-Id": "22222222-2222-2222-2222-222222222222",
        "X-User-Role": "MANAGER",
    }
    reject_payload = {"reason": "Receipt was illegible, please resubmit with clear copy"}

    response = client.post(
        f"/api/v1/expenses/{expense_id}/reject",
        json=reject_payload,
        headers=manager_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == expense_id
    assert data["status"] == "REJECTED"
    assert data["currency"] == "INR"
    assert "employee_id" in data
    assert "amount" in data
    assert "category" in data
    assert "description" in data
    assert "created_at" in data
    assert "updated_at" in data

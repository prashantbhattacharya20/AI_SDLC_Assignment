from fastapi.testclient import TestClient

EMPLOYEE_ID = "11111111-1111-1111-1111-111111111111"
MANAGER_ID = "22222222-2222-2222-2222-222222222222"

EMPLOYEE_HEADERS = {
    "X-User-Id": EMPLOYEE_ID,
    "X-User-Role": "EMPLOYEE",
}

MANAGER_HEADERS = {
    "X-User-Id": MANAGER_ID,
    "X-User-Role": "MANAGER",
}


def _seed_expense(client: TestClient) -> str:
    payload = {
        "amount": 3200.00,
        "currency": "INR",
        "category": "Travel",
        "description": "Flight booking for annual conference",
        "expense_date": "2026-11-17",
    }
    resp = client.post("/api/v1/expenses", json=payload, headers=EMPLOYEE_HEADERS)
    assert resp.status_code == 201
    return resp.json()["id"]


def test_list_expenses_contract(client: TestClient):
    _seed_expense(client)

    response = client.get("/api/v1/expenses", headers=EMPLOYEE_HEADERS)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    item = data[0]
    # Check ExpenseResponse schema conformance
    assert "id" in item
    assert "employee_id" in item
    assert "amount" in item
    assert "currency" in item
    assert item["currency"] == "INR"
    assert "category" in item
    assert "description" in item
    assert "expense_date" in item
    assert "status" in item
    assert "created_at" in item
    assert "updated_at" in item


def test_get_expense_detail_contract(client: TestClient):
    expense_id = _seed_expense(client)

    response = client.get(f"/api/v1/expenses/{expense_id}", headers=EMPLOYEE_HEADERS)
    assert response.status_code == 200

    data = response.json()
    # Check ExpenseDetailResponse schema conformance
    assert data["id"] == expense_id
    assert data["employee_id"] == EMPLOYEE_ID
    assert float(data["amount"]) == 3200.00
    assert data["currency"] == "INR"
    assert "approval_actions" in data
    assert isinstance(data["approval_actions"], list)
    assert "audit_trail" in data
    assert isinstance(data["audit_trail"], list)
    assert len(data["audit_trail"]) >= 1

    log = data["audit_trail"][0]
    assert "id" in log
    assert "actor_id" in log
    assert "action_type" in log
    assert "resulting_state" in log
    assert "timestamp" in log

"""
Verification of all scenarios described in specs/001-expense-management/quickstart.md.
"""

from fastapi.testclient import TestClient

ALICE_HEADERS = {
    "X-User-Id": "11111111-1111-1111-1111-111111111111",
    "X-User-Role": "EMPLOYEE",
}

BOB_HEADERS = {
    "X-User-Id": "22222222-2222-2222-2222-222222222222",
    "X-User-Role": "MANAGER",
}


def test_quickstart_scenario_a_employee_submit(client: TestClient):
    """Scenario A: Employee Submits an Expense (Happy Path)."""
    payload = {
        "amount": 750.50,
        "currency": "INR",
        "category": "Meals",
        "description": "Lunch meeting with product design team",
        "expense_date": "2026-11-18",
    }
    response = client.post("/api/v1/expenses", json=payload, headers=ALICE_HEADERS)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "SUBMITTED"
    assert data["currency"] == "INR"
    assert float(data["amount"]) == 750.50
    assert "id" in data


def test_quickstart_scenario_b_negative_validation_and_self_approval(client: TestClient):
    """Scenario B: Negative Validation & Self-Approval Prevention."""
    # 1. Negative amount
    bad_payload = {
        "amount": -500.00,
        "currency": "INR",
        "category": "Travel",
        "description": "Invalid negative test",
        "expense_date": "2026-11-18",
    }
    neg_response = client.post("/api/v1/expenses", json=bad_payload, headers=ALICE_HEADERS)
    assert neg_response.status_code in (400, 422)

    # 2. Bob (Manager) creates an expense
    bob_payload = {
        "amount": 1200.00,
        "currency": "INR",
        "category": "Equipment",
        "description": "Keyboard purchase",
        "expense_date": "2026-11-18",
    }
    bob_exp_resp = client.post("/api/v1/expenses", json=bob_payload, headers=BOB_HEADERS)
    assert bob_exp_resp.status_code == 201
    bob_exp_id = bob_exp_resp.json()["id"]

    # Bob attempts self-approval
    self_app_resp = client.post(
        f"/api/v1/expenses/{bob_exp_id}/approve",
        headers=BOB_HEADERS,
    )
    assert self_app_resp.status_code == 403
    assert "Self-approval is strictly prohibited" in self_app_resp.json()["detail"]


def test_quickstart_scenario_c_rejection_and_immutability(client: TestClient):
    """Scenario C: Manager Rejection & Immutability Verification."""
    # Alice submits
    payload = {
        "amount": 1800.00,
        "currency": "INR",
        "category": "Meals",
        "description": "Team lunch celebration",
        "expense_date": "2026-11-18",
    }
    alice_resp = client.post("/api/v1/expenses", json=payload, headers=ALICE_HEADERS)
    assert alice_resp.status_code == 201
    alice_exp_id = alice_resp.json()["id"]

    # Bob rejects
    reject_resp = client.post(
        f"/api/v1/expenses/{alice_exp_id}/reject",
        json={"reason": "Exceeds per-diem meals limit for team lunches."},
        headers=BOB_HEADERS,
    )
    assert reject_resp.status_code == 200
    assert reject_resp.json()["status"] == "REJECTED"

    # Immutability verification: PUT and DELETE are not supported
    put_resp = client.put(f"/api/v1/expenses/{alice_exp_id}", headers=ALICE_HEADERS)
    assert put_resp.status_code in (404, 405)

    del_resp = client.delete(f"/api/v1/expenses/{alice_exp_id}", headers=ALICE_HEADERS)
    assert del_resp.status_code in (404, 405)

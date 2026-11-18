from fastapi.testclient import TestClient

EMPLOYEE_ID = "11111111-1111-1111-1111-111111111111"
MANAGER_BOB_ID = "22222222-2222-2222-2222-222222222222"
MANAGER_CHARLIE_ID = "33333333-3333-3333-3333-333333333333"

EMPLOYEE_HEADERS = {
    "X-User-Id": EMPLOYEE_ID,
    "X-User-Role": "EMPLOYEE",
}

MANAGER_BOB_HEADERS = {
    "X-User-Id": MANAGER_BOB_ID,
    "X-User-Role": "MANAGER",
}

MANAGER_CHARLIE_HEADERS = {
    "X-User-Id": MANAGER_CHARLIE_ID,
    "X-User-Role": "MANAGER",
}


def _submit_expense(client: TestClient, employee_headers=None) -> str:
    headers = employee_headers or EMPLOYEE_HEADERS
    payload = {
        "amount": 2500.00,
        "currency": "INR",
        "category": "Equipment",
        "description": "Ergonomic wireless keyboard and mouse",
        "expense_date": "2026-11-18",
    }
    resp = client.post("/api/v1/expenses", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()["id"]


def test_manager_approve_expense_success(client: TestClient):
    expense_id = _submit_expense(client)

    approve_resp = client.post(
        f"/api/v1/expenses/{expense_id}/approve",
        json={"comments": "Approved. Necessary peripheral gear."},
        headers=MANAGER_BOB_HEADERS,
    )
    assert approve_resp.status_code == 200
    data = approve_resp.json()
    assert data["status"] == "APPROVED"
    assert data["id"] == expense_id

    # Verify via details endpoint
    detail_resp = client.get(f"/api/v1/expenses/{expense_id}", headers=MANAGER_BOB_HEADERS)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["status"] == "APPROVED"
    assert len(detail["approval_actions"]) == 1
    assert detail["approval_actions"][0]["decision"] == "APPROVE"
    assert detail["approval_actions"][0]["approver_id"] == MANAGER_BOB_ID
    assert detail["approval_actions"][0]["comments"] == "Approved. Necessary peripheral gear."

    # Verify audit trail contains SUBMIT and APPROVE
    actions = [log["action_type"] for log in detail["audit_trail"]]
    assert "SUBMIT" in actions
    assert "APPROVE" in actions


def test_manager_reject_expense_success(client: TestClient):
    expense_id = _submit_expense(client)

    reject_resp = client.post(
        f"/api/v1/expenses/{expense_id}/reject",
        json={"reason": "Category does not match item description"},
        headers=MANAGER_BOB_HEADERS,
    )
    assert reject_resp.status_code == 200
    data = reject_resp.json()
    assert data["status"] == "REJECTED"

    # Verify via details endpoint
    detail_resp = client.get(f"/api/v1/expenses/{expense_id}", headers=MANAGER_BOB_HEADERS)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["status"] == "REJECTED"
    assert len(detail["approval_actions"]) == 1
    assert detail["approval_actions"][0]["decision"] == "REJECT"
    assert detail["approval_actions"][0]["comments"] == "Category does not match item description"

    actions = [log["action_type"] for log in detail["audit_trail"]]
    assert "SUBMIT" in actions
    assert "REJECT" in actions


def test_manager_reject_missing_or_short_reason_fails(client: TestClient):
    expense_id = _submit_expense(client)

    # Missing reason
    resp1 = client.post(
        f"/api/v1/expenses/{expense_id}/reject",
        json={},
        headers=MANAGER_BOB_HEADERS,
    )
    assert resp1.status_code == 422

    # Short reason (< 5 chars)
    resp2 = client.post(
        f"/api/v1/expenses/{expense_id}/reject",
        json={"reason": "No"},
        headers=MANAGER_BOB_HEADERS,
    )
    assert resp2.status_code in (400, 422)


def test_employee_cannot_approve_or_reject(client: TestClient):
    expense_id = _submit_expense(client)

    # Employee tries to approve
    resp1 = client.post(
        f"/api/v1/expenses/{expense_id}/approve",
        json={"comments": "Approve myself"},
        headers=EMPLOYEE_HEADERS,
    )
    assert resp1.status_code == 403

    # Employee tries to reject
    resp2 = client.post(
        f"/api/v1/expenses/{expense_id}/reject",
        json={"reason": "Rejecting as employee"},
        headers=EMPLOYEE_HEADERS,
    )
    assert resp2.status_code == 403


def test_manager_self_approval_prohibited(client: TestClient):
    # Manager Bob submits an expense as an employee
    manager_as_submitter_headers = {
        "X-User-Id": MANAGER_BOB_ID,
        "X-User-Role": "MANAGER",
    }
    expense_id = _submit_expense(client, employee_headers=manager_as_submitter_headers)

    # Manager Bob attempts to approve their own expense
    approve_resp = client.post(
        f"/api/v1/expenses/{expense_id}/approve",
        json={"comments": "Approving my own claim"},
        headers=MANAGER_BOB_HEADERS,
    )
    assert approve_resp.status_code == 403
    assert "Self-approval is strictly prohibited" in approve_resp.json()["detail"]

    # Charlie (another manager) should be able to approve Bob's expense
    charlie_resp = client.post(
        f"/api/v1/expenses/{expense_id}/approve",
        json={"comments": "Approved by peer manager"},
        headers=MANAGER_CHARLIE_HEADERS,
    )
    assert charlie_resp.status_code == 200
    assert charlie_resp.json()["status"] == "APPROVED"


def test_terminal_state_locking(client: TestClient):
    expense_id = _submit_expense(client)

    # First approve it
    resp = client.post(
        f"/api/v1/expenses/{expense_id}/approve",
        json={"comments": "Initial approval"},
        headers=MANAGER_BOB_HEADERS,
    )
    assert resp.status_code == 200

    # Try to approve again -> 409
    resp_approve_again = client.post(
        f"/api/v1/expenses/{expense_id}/approve",
        json={"comments": "Second approval"},
        headers=MANAGER_CHARLIE_HEADERS,
    )
    assert resp_approve_again.status_code == 409

    # Try to reject an approved expense -> 409
    resp_reject_approved = client.post(
        f"/api/v1/expenses/{expense_id}/reject",
        json={"reason": "Trying to reject after approval"},
        headers=MANAGER_CHARLIE_HEADERS,
    )
    assert resp_reject_approved.status_code == 409


def test_approve_reject_nonexistent_expense(client: TestClient):
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp1 = client.post(
        f"/api/v1/expenses/{fake_id}/approve",
        json={"comments": "Approve non-existent"},
        headers=MANAGER_BOB_HEADERS,
    )
    assert resp1.status_code == 404

    resp2 = client.post(
        f"/api/v1/expenses/{fake_id}/reject",
        json={"reason": "Reject non-existent"},
        headers=MANAGER_BOB_HEADERS,
    )
    assert resp2.status_code == 404

from datetime import date, timedelta

from fastapi.testclient import TestClient

ALICE_ID = "11111111-1111-1111-1111-111111111111"
BOB_ID = "22222222-2222-2222-2222-222222222222"
CHARLIE_ID = "33333333-3333-3333-3333-333333333333"

ALICE_HEADERS = {
    "X-User-Id": ALICE_ID,
    "X-User-Role": "EMPLOYEE",
}

BOB_HEADERS = {
    "X-User-Id": BOB_ID,
    "X-User-Role": "MANAGER",
}

CHARLIE_HEADERS = {
    "X-User-Id": CHARLIE_ID,
    "X-User-Role": "MANAGER",
}


def test_employee_sees_only_own_expenses(client: TestClient):
    # Alice submits an expense
    resp1 = client.post(
        "/api/v1/expenses",
        json={
            "amount": 500.00,
            "currency": "INR",
            "category": "Meals",
            "description": "Alice breakfast",
            "expense_date": str(date.today()),
        },
        headers=ALICE_HEADERS,
    )
    assert resp1.status_code == 201
    alice_exp_id = resp1.json()["id"]

    # Charlie (using employee role header) submits an expense
    charlie_employee_headers = {
        "X-User-Id": CHARLIE_ID,
        "X-User-Role": "EMPLOYEE",
    }
    resp2 = client.post(
        "/api/v1/expenses",
        json={
            "amount": 1200.00,
            "currency": "INR",
            "category": "Software",
            "description": "Charlie dev tool",
            "expense_date": str(date.today()),
        },
        headers=charlie_employee_headers,
    )
    assert resp2.status_code == 201
    charlie_exp_id = resp2.json()["id"]

    # Alice queries expenses
    alice_list_resp = client.get("/api/v1/expenses", headers=ALICE_HEADERS)
    assert alice_list_resp.status_code == 200
    alice_list = alice_list_resp.json()
    alice_ids = [item["id"] for item in alice_list]
    assert alice_exp_id in alice_ids
    assert charlie_exp_id not in alice_ids


def test_manager_sees_all_submitted_expenses(client: TestClient):
    # Alice submits an expense
    resp_alice = client.post(
        "/api/v1/expenses",
        json={
            "amount": 800.00,
            "currency": "INR",
            "category": "Utilities",
            "description": "Office broadband share",
            "expense_date": str(date.today()),
        },
        headers=ALICE_HEADERS,
    )
    assert resp_alice.status_code == 201
    alice_exp_id = resp_alice.json()["id"]

    # Manager Bob queries expenses
    mgr_list_resp = client.get("/api/v1/expenses", headers=BOB_HEADERS)
    assert mgr_list_resp.status_code == 200
    mgr_list = mgr_list_resp.json()
    mgr_ids = [item["id"] for item in mgr_list]
    assert alice_exp_id in mgr_ids


def test_filter_expenses_by_status(client: TestClient):
    # Create two expenses: one to approve, one to leave submitted
    resp1 = client.post(
        "/api/v1/expenses",
        json={
            "amount": 350.00,
            "currency": "INR",
            "category": "Meals",
            "description": "Coffee with candidate",
            "expense_date": str(date.today()),
        },
        headers=ALICE_HEADERS,
    )
    assert resp1.status_code == 201
    exp_to_approve = resp1.json()["id"]

    resp2 = client.post(
        "/api/v1/expenses",
        json={
            "amount": 450.00,
            "currency": "INR",
            "category": "Meals",
            "description": "Team snacks",
            "expense_date": str(date.today()),
        },
        headers=ALICE_HEADERS,
    )
    assert resp2.status_code == 201
    exp_submitted = resp2.json()["id"]

    # Approve the first one
    app_resp = client.post(
        f"/api/v1/expenses/{exp_to_approve}/approve",
        json={"comments": "Approved"},
        headers=BOB_HEADERS,
    )
    assert app_resp.status_code == 200

    # Filter by APPROVED
    approved_list = client.get(
        "/api/v1/expenses?status=APPROVED",
        headers=BOB_HEADERS,
    ).json()
    approved_ids = [e["id"] for e in approved_list]
    assert exp_to_approve in approved_ids
    assert exp_submitted not in approved_ids

    # Filter by SUBMITTED
    submitted_list = client.get(
        "/api/v1/expenses?status=SUBMITTED",
        headers=BOB_HEADERS,
    ).json()
    submitted_ids = [e["id"] for e in submitted_list]
    assert exp_submitted in submitted_ids
    assert exp_to_approve not in submitted_ids


def test_filter_expenses_by_category_and_date(client: TestClient):
    today = date.today()
    yesterday = today - timedelta(days=1)

    # Equipment expense on yesterday
    resp_equip = client.post(
        "/api/v1/expenses",
        json={
            "amount": 1500.00,
            "currency": "INR",
            "category": "Equipment",
            "description": "Monitor stand",
            "expense_date": str(yesterday),
        },
        headers=ALICE_HEADERS,
    )
    equip_id = resp_equip.json()["id"]

    # Meals expense on today
    resp_meals = client.post(
        "/api/v1/expenses",
        json={
            "amount": 600.00,
            "currency": "INR",
            "category": "Meals",
            "description": "Client dinner",
            "expense_date": str(today),
        },
        headers=ALICE_HEADERS,
    )
    meals_id = resp_meals.json()["id"]

    # Filter by category=Equipment
    equip_filter = client.get(
        "/api/v1/expenses?category=Equipment",
        headers=ALICE_HEADERS,
    ).json()
    equip_ids = [e["id"] for e in equip_filter]
    assert equip_id in equip_ids
    assert meals_id not in equip_ids

    # Filter by date range matching only today
    date_filter = client.get(
        f"/api/v1/expenses?start_date={today}&end_date={today}",
        headers=ALICE_HEADERS,
    ).json()
    date_ids = [e["id"] for e in date_filter]
    assert meals_id in date_ids
    assert equip_id not in date_ids


def test_employee_cannot_view_other_employee_detail(client: TestClient):
    # Charlie submits expense as employee
    charlie_headers = {
        "X-User-Id": CHARLIE_ID,
        "X-User-Role": "EMPLOYEE",
    }
    resp = client.post(
        "/api/v1/expenses",
        json={
            "amount": 999.00,
            "currency": "INR",
            "category": "Other",
            "description": "Charlie private claim",
            "expense_date": str(date.today()),
        },
        headers=charlie_headers,
    )
    exp_id = resp.json()["id"]

    # Alice tries to view Charlie's expense
    alice_resp = client.get(f"/api/v1/expenses/{exp_id}", headers=ALICE_HEADERS)
    assert alice_resp.status_code == 403

    # Manager Bob can view it
    bob_resp = client.get(f"/api/v1/expenses/{exp_id}", headers=BOB_HEADERS)
    assert bob_resp.status_code == 200
    assert bob_resp.json()["id"] == exp_id


def test_get_nonexistent_expense_detail(client: TestClient):
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = client.get(f"/api/v1/expenses/{fake_id}", headers=ALICE_HEADERS)
    assert resp.status_code == 404

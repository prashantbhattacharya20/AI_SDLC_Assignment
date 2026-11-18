from datetime import date, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models.audit import AuditLogEntry
from src.models.expense import Expense


def test_submit_valid_expense_success(client: TestClient, db_session: Session):
    headers = {
        "X-User-Id": "11111111-1111-1111-1111-111111111111",
        "X-User-Role": "EMPLOYEE",
    }
    payload = {
        "amount": 1250.75,
        "category": "Travel",
        "description": "Taxi fare to regional client meeting",
        "expense_date": date.today().isoformat(),
    }
    response = client.post("/api/v1/expenses", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "SUBMITTED"
    assert data["currency"] == "INR"
    assert data["category"] == "Travel"

    # Verify database persistence
    expense = db_session.query(Expense).filter(Expense.id == data["id"]).first()
    assert expense is not None
    assert expense.amount == Decimal("1250.75")
    assert expense.status == "SUBMITTED"

    # Verify audit log entry
    audit = db_session.query(AuditLogEntry).filter(AuditLogEntry.expense_id == data["id"]).first()
    assert audit is not None
    assert audit.action_type == "SUBMIT"
    assert audit.resulting_state == "SUBMITTED"
    assert audit.actor_id == "11111111-1111-1111-1111-111111111111"


def test_submit_negative_amount_fails(client: TestClient):
    headers = {
        "X-User-Id": "11111111-1111-1111-1111-111111111111",
        "X-User-Role": "EMPLOYEE",
    }
    payload = {
        "amount": -50.00,
        "category": "Meals",
        "description": "Negative amount test",
        "expense_date": date.today().isoformat(),
    }
    response = client.post("/api/v1/expenses", json=payload, headers=headers)
    assert response.status_code in (400, 422)


def test_submit_zero_amount_fails(client: TestClient):
    headers = {
        "X-User-Id": "11111111-1111-1111-1111-111111111111",
        "X-User-Role": "EMPLOYEE",
    }
    payload = {
        "amount": 0.00,
        "category": "Meals",
        "description": "Zero amount test",
        "expense_date": date.today().isoformat(),
    }
    response = client.post("/api/v1/expenses", json=payload, headers=headers)
    assert response.status_code in (400, 422)


def test_submit_more_than_two_decimals_fails(client: TestClient):
    headers = {
        "X-User-Id": "11111111-1111-1111-1111-111111111111",
        "X-User-Role": "EMPLOYEE",
    }
    payload = {
        "amount": 45.678,
        "category": "Meals",
        "description": "Fractional paise test",
        "expense_date": date.today().isoformat(),
    }
    response = client.post("/api/v1/expenses", json=payload, headers=headers)
    assert response.status_code in (400, 422)


def test_submit_future_date_fails(client: TestClient):
    headers = {
        "X-User-Id": "11111111-1111-1111-1111-111111111111",
        "X-User-Role": "EMPLOYEE",
    }
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    payload = {
        "amount": 100.00,
        "category": "Equipment",
        "description": "Future date test",
        "expense_date": tomorrow,
    }
    response = client.post("/api/v1/expenses", json=payload, headers=headers)
    assert response.status_code in (400, 422)


def test_submit_invalid_category_fails(client: TestClient):
    headers = {
        "X-User-Id": "11111111-1111-1111-1111-111111111111",
        "X-User-Role": "EMPLOYEE",
    }
    payload = {
        "amount": 100.00,
        "category": "CryptoLuxury",
        "description": "Invalid category test",
        "expense_date": date.today().isoformat(),
    }
    response = client.post("/api/v1/expenses", json=payload, headers=headers)
    assert response.status_code in (400, 422)


def test_submit_missing_auth_headers_fails(client: TestClient):
    payload = {
        "amount": 100.00,
        "category": "Software",
        "description": "Missing auth headers test",
        "expense_date": date.today().isoformat(),
    }
    response = client.post("/api/v1/expenses", json=payload)
    assert response.status_code == 401

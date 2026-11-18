# Quickstart Validation Guide: Expense Management System (MVP)

**Feature**: Expense Management System (MVP)
**Branch**: `001-expense-management`
**Date**: 2026-11-18
**Status**: Ready for Validation

This guide provides runnable scenarios to validate that the Expense Management System satisfies all functional and non-functional requirements end-to-end.

---

## 1. Prerequisites & Environment Setup

- Python 3.11+
- Virtual environment with dependencies installed:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

---

## 2. Test Execution Scenarios

### Scenario 1: Run Full Automated Verification Suite
Execute unit, contract, and integration tests ensuring 100% passing state:
```bash
# Run all test suites
pytest -v

# Run with coverage report
pytest --cov=src tests/
```
**Expected Outcome**:
- Unit tests verify field validations (positive amount in INR, two-decimal precision, date constraint, category enum, self-approval prevention).
- Contract tests verify OpenAPI conformance against [contracts/expenses-api.yaml](contracts/expenses-api.yaml).
- Integration tests verify the full lifecycle: `SUBMITTED` → `APPROVED` and `SUBMITTED` → `REJECTED`.

---

## 3. End-to-End API Scenarios

Start the local development server:
```bash
uvicorn src.main:app --reload --port 8000
```
OpenAPI documentation will be accessible at: `http://localhost:8000/docs`

### Seed Personas
- **Alice (Employee)**: `X-User-Id: 11111111-1111-1111-1111-111111111111`, `X-User-Role: EMPLOYEE`
- **Bob (Manager)**: `X-User-Id: 22222222-2222-2222-2222-222222222222`, `X-User-Role: MANAGER`

---

### Scenario A: Employee Submits an Expense (Happy Path)

**Submit Expense**:
```bash
curl -X POST http://localhost:8000/api/v1/expenses \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 11111111-1111-1111-1111-111111111111" \
  -H "X-User-Role: EMPLOYEE" \
  -d '{
    "amount": 750.50,
    "currency": "INR",
    "category": "Meals",
    "description": "Lunch meeting with product design team",
    "expense_date": "2026-11-18"
  }'
```
**Expected Outcome**: HTTP `201 Created`, status is `SUBMITTED`, currency is `INR`, returns UUID `EXPENSE_ID`.

---

### Scenario B: Negative Validation & Self-Approval Prevention

1. **Submit Negative Amount (Should Fail)**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/expenses \
     -H "Content-Type: application/json" \
     -H "X-User-Id: 11111111-1111-1111-1111-111111111111" \
     -H "X-User-Role: EMPLOYEE" \
     -d '{
       "amount": -500.00,
       "currency": "INR",
       "category": "Travel",
       "description": "Invalid negative test",
       "expense_date": "2026-11-18"
     }'
   ```
   **Expected Outcome**: HTTP `400 Bad Request` or `422 Unprocessable Entity` with validation detail `amount must be greater than 0`.

2. **Self-Approval Attempt (Should Fail)**:
   ```bash
   # Bob (Manager) creates an expense
   curl -X POST http://localhost:8000/api/v1/expenses \
     -H "Content-Type: application/json" \
     -H "X-User-Id: 22222222-2222-2222-2222-222222222222" \
     -H "X-User-Role: MANAGER" \
     -d '{
       "amount": 1200.00,
       "currency": "INR",
       "category": "Equipment",
       "description": "Keyboard purchase",
       "expense_date": "2026-11-18"
     }'

   # Bob attempts to approve his own expense
   curl -X POST http://localhost:8000/api/v1/expenses/{BOB_EXPENSE_ID}/approve \
     -H "X-User-Id: 22222222-2222-2222-2222-222222222222" \
     -H "X-User-Role: MANAGER"
   ```
   **Expected Outcome**: HTTP `403 Forbidden` with detail `Self-approval is strictly prohibited`.

---

### Scenario C: Manager Rejection & Immutability Verification

1. **Manager Rejects with Justification**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/expenses/{ALICE_EXPENSE_ID}/reject \
     -H "Content-Type: application/json" \
     -H "X-User-Id: 22222222-2222-2222-2222-222222222222" \
     -H "X-User-Role: MANAGER" \
     -d '{
       "reason": "Exceeds per-diem meals limit for team lunches."
     }'
   ```
   **Expected Outcome**: HTTP `200 OK`, status transitions to `REJECTED`.

2. **Immutability Verification**:
   - The API strictly excludes `PUT` (update) and `DELETE` endpoints per the approved MVP specification.
   - Once submitted, expenses cannot be altered or removed; attempting HTTP `PUT` or `DELETE` to `/api/v1/expenses/{id}` returns HTTP `405 Method Not Allowed`.

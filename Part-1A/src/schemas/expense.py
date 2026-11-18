from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.schemas.common import ExpenseCategory, ExpenseStatus


class ExpenseCreateRequest(BaseModel):
    """
    Schema for submitting a new expense.
    Canonical constraints citation: data-model.md#41-expense
    """

    amount: Decimal = Field(
        ...,
        gt=Decimal("0.00"),
        le=Decimal("1000000.00"),
        description="Expense amount in INR with maximum 2 decimal places (paise)",
    )
    currency: str = Field(default="INR", min_length=3, max_length=3)
    category: ExpenseCategory
    description: str = Field(..., min_length=3, max_length=500)
    expense_date: date

    @field_validator("amount")
    @classmethod
    def validate_amount_precision(cls, v: Decimal) -> Decimal:
        if v.as_tuple().exponent < -2:
            raise ValueError("Amount cannot have more than 2 decimal places (fractional paise)")
        return v

    @field_validator("expense_date")
    @classmethod
    def validate_expense_date_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Expense date cannot be in the future")
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        return v.upper()


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    employee_id: str
    amount: Decimal
    currency: str
    category: ExpenseCategory
    description: str
    expense_date: date
    status: ExpenseStatus
    created_at: datetime
    updated_at: datetime


class ApprovalActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    approver_id: str
    decision: str
    comments: Optional[str] = None
    created_at: datetime


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    actor_id: str
    action_type: str
    previous_state: Optional[str] = None
    resulting_state: str
    notes: Optional[str] = None
    timestamp: datetime


class ExpenseDetailResponse(ExpenseResponse):
    approval_actions: List[ApprovalActionResponse] = Field(default_factory=list)
    audit_trail: List[AuditLogResponse] = Field(default_factory=list)

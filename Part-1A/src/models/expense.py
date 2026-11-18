from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.schemas.common import ExpenseStatus


class Expense(Base):
    """
    Business expense claim entity.
    Canonical schema citation: data-model.md#41-expense
    """

    __tablename__ = "expenses"

    # Expense.id
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Expense.employee_id
    employee_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True, nullable=False
    )
    # Expense.amount: Decimal with max 2 decimal places (paise)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    # Expense.currency: default INR
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    # Expense.category: Travel, Meals, Equipment, Software, Utilities, Other
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    # Expense.description
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    # Expense.expense_date: Date <= today()
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    # Expense.status: SUBMITTED | APPROVED | REJECTED
    status: Mapped[str] = mapped_column(
        String(20), default=ExpenseStatus.SUBMITTED.value, nullable=False
    )
    # Expense.created_at
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    # Expense.updated_at
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    employee = relationship("User", foreign_keys=[employee_id])
    approval_actions = relationship(
        "ApprovalAction", back_populates="expense", cascade="all, delete-orphan"
    )
    audit_logs = relationship(
        "AuditLogEntry", foreign_keys="AuditLogEntry.expense_id", cascade="all, delete-orphan"
    )

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class ApprovalAction(Base):
    """
    Approval decision entity.
    Canonical schema citation: data-model.md#42-approvalaction
    """

    __tablename__ = "approval_actions"

    # ApprovalAction.id
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # ApprovalAction.expense_id
    expense_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("expenses.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # ApprovalAction.approver_id
    approver_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True, nullable=False
    )
    # ApprovalAction.decision (APPROVE | REJECT)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    # ApprovalAction.comments (Mandatory if REJECT)
    comments: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    # ApprovalAction.created_at
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    expense = relationship("Expense", back_populates="approval_actions")
    approver = relationship("User", foreign_keys=[approver_id])

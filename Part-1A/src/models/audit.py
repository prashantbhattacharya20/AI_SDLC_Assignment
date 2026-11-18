import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class AuditLogEntry(Base):
    """
    Audit log entry recording all status transitions and actions.
    Canonical schema citation: data-model.md#43-auditlogentry
    """

    __tablename__ = "audit_log_entries"

    # AuditLogEntry.id
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # AuditLogEntry.expense_id (references Expense.id)
    expense_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("expenses.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # AuditLogEntry.actor_id (references User.id)
    actor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True, nullable=False
    )
    # AuditLogEntry.action_type (SUBMIT | APPROVE | REJECT)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # AuditLogEntry.previous_state (Prior status)
    previous_state: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # AuditLogEntry.resulting_state (New status)
    resulting_state: Mapped[str] = mapped_column(String(20), nullable=False)
    # AuditLogEntry.notes (Optional reason/comments)
    notes: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    # AuditLogEntry.timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

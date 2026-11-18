from typing import Optional

from sqlalchemy.orm import Session

from src.models.audit import AuditLogEntry


class AuditService:
    @staticmethod
    def record_event(
        db: Session,
        expense_id: str,
        actor_id: str,
        action_type: str,
        resulting_state: str,
        previous_state: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> AuditLogEntry:
        """
        Record an immutable audit log entry in the database.
        """
        entry = AuditLogEntry(
            expense_id=expense_id,
            actor_id=actor_id,
            action_type=action_type,
            previous_state=previous_state,
            resulting_state=resulting_state,
            notes=notes,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

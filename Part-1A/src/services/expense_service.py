from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from src.api.errors import DomainError, SelfApprovalError, StateTransitionError
from src.models.approval import ApprovalAction
from src.models.expense import Expense
from src.models.user import User
from src.schemas.common import DecisionAction, ExpenseCategory, ExpenseStatus, UserRole
from src.schemas.expense import ExpenseCreateRequest
from src.services.audit_service import AuditService


class ExpenseService:
    @staticmethod
    def submit_expense(
        db: Session,
        employee: User,
        data: ExpenseCreateRequest,
    ) -> Expense:
        """
        Record and submit a new expense claim.
        Initial state is strictly SUBMITTED.
        """
        expense = Expense(
            employee_id=employee.id,
            amount=data.amount,
            currency=data.currency,
            category=data.category.value,
            description=data.description,
            expense_date=data.expense_date,
            status=ExpenseStatus.SUBMITTED.value,
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)

        # Record audit log entry
        AuditService.record_event(
            db=db,
            expense_id=expense.id,
            actor_id=employee.id,
            action_type="SUBMIT",
            resulting_state=ExpenseStatus.SUBMITTED.value,
            previous_state=None,
            notes=f"Expense submitted by {employee.full_name}",
        )
        return expense

    @staticmethod
    def get_expense_by_id(
        db: Session,
        expense_id: str,
        current_user: User,
    ) -> Expense:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            raise DomainError("Expense not found", status_code=404)

        # Authorization: Employees can only view their own expenses
        if current_user.role == UserRole.EMPLOYEE.value and expense.employee_id != current_user.id:
            raise DomainError("Access forbidden to requested expense", status_code=403)

        return expense

    @staticmethod
    def list_expenses(
        db: Session,
        current_user: User,
        status: Optional[ExpenseStatus] = None,
        category: Optional[ExpenseCategory] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Expense]:
        query = db.query(Expense)

        # Scoping: Employees see only own expenses; Managers can view all submitted
        if current_user.role == UserRole.EMPLOYEE.value:
            query = query.filter(Expense.employee_id == current_user.id)

        if status:
            query = query.filter(Expense.status == status.value)
        if category:
            query = query.filter(Expense.category == category.value)
        if start_date:
            query = query.filter(Expense.expense_date >= start_date)
        if end_date:
            query = query.filter(Expense.expense_date <= end_date)

        return query.order_by(Expense.created_at.desc()).all()

    @staticmethod
    def approve_expense(
        db: Session,
        expense_id: str,
        approver: User,
        comments: Optional[str] = None,
    ) -> Expense:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            raise DomainError("Expense not found", status_code=404)

        # Terminal state check
        if expense.status in (ExpenseStatus.APPROVED.value, ExpenseStatus.REJECTED.value):
            raise StateTransitionError(
                f"Cannot transition expense in terminal state: {expense.status}"
            )

        if expense.status != ExpenseStatus.SUBMITTED.value:
            raise StateTransitionError("Expense must be in SUBMITTED state to approve")

        # Self-approval check
        if expense.employee_id == approver.id:
            raise SelfApprovalError("Self-approval is strictly prohibited")

        # Execute transition
        previous_status = expense.status
        expense.status = ExpenseStatus.APPROVED.value

        # Record approval decision
        action = ApprovalAction(
            expense_id=expense.id,
            approver_id=approver.id,
            decision=DecisionAction.APPROVE.value,
            comments=comments,
        )
        db.add(action)
        db.commit()
        db.refresh(expense)

        # Record audit log
        AuditService.record_event(
            db=db,
            expense_id=expense.id,
            actor_id=approver.id,
            action_type="APPROVE",
            previous_state=previous_status,
            resulting_state=ExpenseStatus.APPROVED.value,
            notes=comments,
        )
        return expense

    @staticmethod
    def reject_expense(
        db: Session,
        expense_id: str,
        approver: User,
        reason: str,
    ) -> Expense:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            raise DomainError("Expense not found", status_code=404)

        # Validate mandatory rejection comment
        if not reason or len(reason.strip()) < 5:
            raise DomainError(
                "A rejection reason with at least 5 characters is required",
                status_code=400,
            )

        # Terminal state check
        if expense.status in (ExpenseStatus.APPROVED.value, ExpenseStatus.REJECTED.value):
            raise StateTransitionError(
                f"Cannot transition expense in terminal state: {expense.status}"
            )

        if expense.status != ExpenseStatus.SUBMITTED.value:
            raise StateTransitionError("Expense must be in SUBMITTED state to reject")

        # Self-rejection / self-approval prevention
        if expense.employee_id == approver.id:
            raise SelfApprovalError("Self-review is strictly prohibited")

        # Execute transition
        previous_status = expense.status
        expense.status = ExpenseStatus.REJECTED.value

        # Record approval decision
        action = ApprovalAction(
            expense_id=expense.id,
            approver_id=approver.id,
            decision=DecisionAction.REJECT.value,
            comments=reason,
        )
        db.add(action)
        db.commit()
        db.refresh(expense)

        # Record audit log
        AuditService.record_event(
            db=db,
            expense_id=expense.id,
            actor_id=approver.id,
            action_type="REJECT",
            previous_state=previous_status,
            resulting_state=ExpenseStatus.REJECTED.value,
            notes=reason,
        )
        return expense

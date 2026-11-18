from datetime import date
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_user, require_manager
from src.database import get_db
from src.models.user import User
from src.schemas.approval import ApprovalRequest, RejectionRequest
from src.schemas.common import ExpenseCategory, ExpenseStatus
from src.schemas.expense import (
    ApprovalActionResponse,
    AuditLogResponse,
    ExpenseCreateRequest,
    ExpenseDetailResponse,
    ExpenseResponse,
)
from src.services.expense_service import ExpenseService

router = APIRouter(prefix="/api/v1/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def submit_expense(
    data: ExpenseCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Submit a new expense claim.
    """
    expense = ExpenseService.submit_expense(db=db, employee=current_user, data=data)
    return expense


@router.get("", response_model=List[ExpenseResponse])
def list_expenses(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    status: Optional[ExpenseStatus] = Query(default=None),
    category: Optional[ExpenseCategory] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
):
    """
    List expenses for current employee, or all submitted expenses for managers.
    """
    return ExpenseService.list_expenses(
        db=db,
        current_user=current_user,
        status=status,
        category=category,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/{expense_id}", response_model=ExpenseDetailResponse)
def get_expense(
    expense_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Retrieve single expense with approval actions and audit trail.
    """
    expense = ExpenseService.get_expense_by_id(
        db=db, expense_id=expense_id, current_user=current_user
    )

    approval_actions = [
        ApprovalActionResponse.model_validate(action) for action in expense.approval_actions
    ]
    audit_trail = [AuditLogResponse.model_validate(log) for log in expense.audit_logs]

    response_data = ExpenseDetailResponse.model_validate(expense)
    response_data.approval_actions = approval_actions
    response_data.audit_trail = audit_trail
    return response_data


@router.post("/{expense_id}/approve", response_model=ExpenseResponse)
def approve_expense(
    expense_id: str,
    manager: Annotated[User, Depends(require_manager)],
    data: Optional[ApprovalRequest] = None,
    db: Session = Depends(get_db),
):
    """
    Approve a submitted expense. Caller must have MANAGER role and not be submitter.
    """
    comments = data.comments if data else None
    return ExpenseService.approve_expense(
        db=db,
        expense_id=expense_id,
        approver=manager,
        comments=comments,
    )


@router.post("/{expense_id}/reject", response_model=ExpenseResponse)
def reject_expense(
    expense_id: str,
    data: RejectionRequest,
    manager: Annotated[User, Depends(require_manager)],
    db: Session = Depends(get_db),
):
    """
    Reject a submitted expense. Requires a non-empty explanation.
    """
    return ExpenseService.reject_expense(
        db=db,
        expense_id=expense_id,
        approver=manager,
        reason=data.reason,
    )

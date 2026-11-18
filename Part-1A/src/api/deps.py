from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.schemas.common import UserRole


def get_current_user(
    x_user_id: Annotated[Optional[str], Header()] = None,
    x_user_role: Annotated[Optional[str], Header()] = None,
    db: Session = Depends(get_db),
) -> User:
    if not x_user_id or not x_user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing required authentication headers: X-User-Id and X-User-Role",
        )

    # Validate role enum
    try:
        validated_role = UserRole(x_user_role)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid X-User-Role header: {x_user_role}. Must be EMPLOYEE or MANAGER",
        ) from err

    # Check database for user; create on-the-fly if not found to support test personas seamlessly
    user = db.query(User).filter(User.id == x_user_id).first()
    if not user:
        user = User(
            id=x_user_id,
            email=f"user_{x_user_id[:8]}@example.com",
            full_name=f"User {x_user_id[:8]}",
            role=validated_role.value,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


def require_manager(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role != UserRole.MANAGER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires MANAGER role",
        )
    return current_user

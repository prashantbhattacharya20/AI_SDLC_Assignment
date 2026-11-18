import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.schemas.common import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default=UserRole.EMPLOYEE.value, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )


# Standard Seed Personas for Testing & Development
SEED_USERS = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "alice@example.com",
        "full_name": "Alice Employee",
        "role": UserRole.EMPLOYEE.value,
        "is_active": True,
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "email": "bob@example.com",
        "full_name": "Bob Manager",
        "role": UserRole.MANAGER.value,
        "is_active": True,
    },
    {
        "id": "33333333-3333-3333-3333-333333333333",
        "email": "charlie@example.com",
        "full_name": "Charlie Manager",
        "role": UserRole.MANAGER.value,
        "is_active": True,
    },
]

from typing import Optional

from pydantic import BaseModel, Field


class ApprovalRequest(BaseModel):
    comments: Optional[str] = Field(default=None, max_length=1000)


class RejectionRequest(BaseModel):
    reason: str = Field(..., min_length=5, max_length=1000)

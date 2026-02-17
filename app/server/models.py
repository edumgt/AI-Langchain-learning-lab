from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Literal, Optional

class ChatRequest(BaseModel):
    q: str = Field(min_length=1)
    mode: Literal["chat","rag","plan"] = "rag"
    top_k: int | None = None
    auto_approve: bool | None = None

class ChatResponse(BaseModel):
    answer: str
    mode: str
    used_docs: list[dict] = Field(default_factory=list)
    pending_action: Optional[dict] = None

class ApproveRequest(BaseModel):
    action_id: str
    approve: bool = True
    token: str | None = None

class ApproveResponse(BaseModel):
    ok: bool
    message: str
    action: dict | None = None

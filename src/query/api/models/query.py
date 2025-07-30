from __future__ import annotations

from typing import List
from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[list[dict]] = None
    documents: Optional[list[str]] = None
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    message: str
    sources: Optional[List[dict]] = None

from __future__ import annotations

from typing import List
from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    documents: Optional[List[str]] = None


class ChatResponse(BaseModel):
    message: str
    sources: Optional[List[str]] = None

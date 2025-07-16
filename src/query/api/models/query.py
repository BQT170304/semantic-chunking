from __future__ import annotations

from typing import List
from typing import Optional

from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = None

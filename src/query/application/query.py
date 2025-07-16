from __future__ import annotations

import asyncio

from api.models.query import AskRequest
from api.models.query import AskResponse
from domain.rag.service import RAG


class AskApplication:
    def __init__(self):
        self.rag = RAG()

    async def ask(self, ask_request: AskRequest) -> AskResponse:
        # Validate input
        if not ask_request.question.strip():
            raise ValueError('Question cannot be empty')

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self.rag.process,
            ask_request.question,
        )

        return AskResponse(
            answer=result['answer'],
            sources=result.get('sources', []),
        )

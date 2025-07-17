from __future__ import annotations

import asyncio

from api.models.query import ChatRequest
from api.models.query import ChatResponse
from domain.rag.service import RAG


class ChatApplication:
    def __init__(self, rag: RAG):
        self.rag = rag

    async def process(self, chat_request: ChatRequest) -> ChatResponse:
        # Validate input
        if not chat_request.message.strip():
            raise ValueError('Message cannot be empty')

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self.rag.process,
            chat_request.message,
        )

        return ChatResponse(
            message=result['message'],
            sources=result.get('sources', []),
        )

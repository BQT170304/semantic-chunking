from __future__ import annotations

from .base import BaseChunkerService
from .base import ChunkerInput
from .base import ChunkerOutput


class ChunkerService(BaseChunkerService):
    def process(self, input_data: ChunkerInput) -> ChunkerOutput:
        return ChunkerOutput(
            chunks=[],
        )

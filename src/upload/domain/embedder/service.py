from __future__ import annotations

from .base import BaseEmbedderService
from .base import EmbedderInput
from .base import EmbedderOutput


class EmbedderService(BaseEmbedderService):
    def process(self, input_data: EmbedderInput) -> EmbedderOutput:
        return EmbedderOutput(
            id='',
            index_name='',
            embedding=[],
        )

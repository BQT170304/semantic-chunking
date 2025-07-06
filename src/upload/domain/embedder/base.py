from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import List
from typing import Optional

from pydantic import BaseModel


class EmbedderInput(BaseModel):
    """Input data for the embedding process."""
    chunk: str
    metadata: dict


class EmbedderOutput(BaseModel):
    """Output data from the embedding process."""
    id: Optional[str] = None
    index_name: Optional[str] = None
    embedding: Optional[List[float]] = None


class BaseEmbedderService(ABC):
    """Abstract base class for embedders."""

    @abstractmethod
    def process(self, input_data: EmbedderInput) -> EmbedderOutput:
        """Generate embeddings for the input text."""
        raise NotImplementedError()

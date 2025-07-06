from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import List
from typing import Optional

from pydantic import BaseModel


class Chunk(BaseModel):
    """Represents a chunk of text."""
    title: str
    content: str
    tag: Optional[str] = None
    metadata: dict  # Filename,...


class ChunkerInput(BaseModel):
    """Input data for the chunking process."""
    text: str
    metadata: dict


class ChunkerOutput(BaseModel):
    """Output data from the chunking process."""
    chunks: List[Chunk]


class BaseChunkerService(ABC):
    """Abstract base class for chunkers."""

    @abstractmethod
    def process(self, input_data: ChunkerInput) -> ChunkerOutput:
        """Chunk the input data into smaller pieces."""
        raise NotImplementedError()

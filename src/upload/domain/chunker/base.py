from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel


class Chunk(BaseModel):
    """Represents a chunk of text."""
    id: int
    content: str
    filename: str
    position: Optional[int] = 0
    tokens: Optional[int] = None
    section_title: str
    type: str
    content_json: Optional[List[Dict[str, str]]] = None
    heading_level: Optional[int] = None


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

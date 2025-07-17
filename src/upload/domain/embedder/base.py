from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Dict
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


class ChunkData(BaseModel):
    """Data model for chunk processing."""
    id: str
    content: str
    filename: str
    position: int
    tokens: int
    section_title: str
    type: str
    content_json: dict
    heading_level: int


class BaseEmbedderService(ABC):
    """Abstract base class for embedders."""

    @abstractmethod
    def process(self, input_data: EmbedderInput) -> EmbedderOutput:
        """Generate embeddings for the input text."""
        raise NotImplementedError()

    @abstractmethod
    def process_chunks(self, chunks: List[ChunkData]) -> bool:
        """Process multiple chunks with embeddings and storage."""
        raise NotImplementedError()


class BaseEmbeddingGenerator(ABC):
    """Abstract base class for embedding generators."""

    @abstractmethod
    def get_embedding_batch(self, texts: List[str]) -> Dict[int, List[float]]:
        """Generate embeddings for multiple texts."""
        raise NotImplementedError()


class BaseStorage(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to storage backend."""
        raise NotImplementedError()

    @abstractmethod
    def create_optimized_index(self) -> None:
        """Create optimized index for storage."""
        raise NotImplementedError()

    @abstractmethod
    def bulk_index_chunks(self, chunks: List[ChunkData], embeddings: Dict[int, List[float]]) -> None:
        """Bulk index chunks with embeddings."""
        raise NotImplementedError()

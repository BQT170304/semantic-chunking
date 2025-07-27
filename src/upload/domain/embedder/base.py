from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel


class EmbedderInput(BaseModel):
    """Input data for the embedding process."""
    chunks: List[ChunkData]
    metadata: dict


class EmbedderOutput(BaseModel):
    """Output data from the embedding process."""
    index_name: Optional[str] = None
    num_embeddings: Optional[int] = 0


class ChunkData(BaseModel):
    """Data model for chunk processing."""
    id: int
    content: str
    section_title: str
    filename: str
    position: Optional[int] = 0
    tokens: Optional[int] = None
    type: Optional[str] = None
    content_json: Optional[List[Dict[str, str]]] = None
    heading_level: Optional[int] = None


class BaseEmbedderService(ABC):
    """Abstract base class for embedders."""

    @abstractmethod
    async def process(self, input_data: EmbedderInput) -> EmbedderOutput:
        """Generate embeddings for the input text."""
        raise NotImplementedError()


class BaseEmbeddingGenerator(ABC):
    """Abstract base class for embedding generators."""

    @abstractmethod
    async def get_embedding_batch(self, texts: List[str]) -> Dict[int, List[float]]:
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

from __future__ import annotations

import logging
from typing import Optional

from domain.chunker import ChunkerInput
from domain.chunker import ChunkerService
from domain.embedder import EmbedderInput
from domain.embedder import EmbedderService
from domain.parser import ParserInput
from domain.parser import ParserService
from fastapi import UploadFile
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class UploadDocumentInput(BaseModel):
    """Input data for the upload document process."""
    file: UploadFile


class UploadDocumentOutput(BaseModel):
    """Output data from the upload document process."""
    status: str
    processing_time: Optional[float] = None


class UploadDocumentApplication:
    """Application service for uploading documents."""

    def __init__(
        self,
        settings: None,  # Code setting sau
        parser: ParserService,
        chunker: ChunkerService,
        embedder: EmbedderService,
    ):
        self.parser = parser
        self.chunker = chunker
        self.embedder = embedder

    def upload_document(self, input_data: UploadDocumentInput) -> UploadDocumentOutput:
        """Upload a document and process it through parsing, chunking, and embedding."""
        parser_input = ParserInput(file=input_data.file)
        parser_output = self.parser.process(parser_input)

        chunker_input = ChunkerInput(text=parser_output.raw_text, metadata=parser_output.metadata)
        chunker_output = self.chunker.process(chunker_input)

        for chunk in chunker_output.chunks:
            embedder_input = EmbedderInput(chunk=chunk.content, metadata=chunk.metadata)
            self.embedder.process(embedder_input)

        return UploadDocumentOutput(status='success')

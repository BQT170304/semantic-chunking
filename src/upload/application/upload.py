from __future__ import annotations

import asyncio
import json
import logging
import time
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from typing import List
from typing import Optional

from domain.chunker import ChunkerInput
from domain.chunker import ChunkerService
from domain.embedder import ChunkData
from domain.embedder import EmbedderInput
from domain.embedder import EmbedderService
from domain.parser import ParserInput
from domain.parser import ParserService
from fastapi import UploadFile
from pydantic import BaseModel
from shared.multiworker_config import get_optimal_worker_count
from shared.multiworker_config import MultiWorkerConfig

logger = logging.getLogger(__name__)


class UploadDocumentInput(BaseModel):
    """Input data for the upload document process."""
    file: UploadFile


class UploadDocumentOutput(BaseModel):
    """Output data from the upload document process."""
    status: str
    message: str
    processed_chunks: int
    embeddings_created: int
    processing_time: float
    filename: str
    error: Optional[str] = None


class UploadMultipleDocumentsInput(BaseModel):
    """Input data for the upload multiple documents process."""
    files: List[UploadFile]
    max_workers: Optional[int] = None
    session_id: Optional[str] = None


class UploadMultipleDocumentsOutput(BaseModel):
    """Output data from the upload multiple documents process."""
    total_files: int
    successful_files: int
    failed_files: int
    total_chunks: int
    total_embeddings: int
    total_processing_time: float
    file_results: List[UploadDocumentOutput]
    errors: List[str]


class UploadDocumentApplication:
    """Application service for document upload and processing."""

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

    def upload_document(self, input_data: UploadDocumentInput, session_id: Optional[str] = None) -> UploadDocumentOutput:
        """Upload a document and process it through parsing, chunking, and embedding."""
        start_time = time.time()
        embeddings_created = 0
        processed_chunks = 0
        status = 'success'

        try:
            logger.info(f'Starting document upload process for file: {input_data.file.filename}')

            logger.info('Step 1: Parsing document...')
            parser_input = ParserInput(file=input_data.file)
            parser_output = self.parser.process(parser_input)
            with open(f'text_{input_data.file.filename}.md', 'w', encoding='utf-8') as f:
                f.write(parser_output.raw_text)

            file_metadata = {
                'filename': parser_output.filename,
                'file_extension': parser_output.file_extension,
                'upload_timestamp': time.time(),
            }

            logger.info('Step 2: Chunking document...')
            chunker_input = ChunkerInput(
                text=str(parser_output.raw_text),
                metadata=file_metadata,
            )
            chunker_output = self.chunker.process(chunker_input)
            chunks_json = [
                chunk.model_dump(mode='json') for chunk in chunker_output.chunks
            ]
            with open(f'chunks_{input_data.file.filename}.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(chunks_json, indent=2, ensure_ascii=False))
            processed_chunks = len(chunker_output.chunks)

            logger.info(f'Created {processed_chunks} chunks')

            logger.info('Step 3: Generating embeddings...')
            try:
                # Convert Chunk objects to ChunkData objects for the embedder
                chunk_data_list = []
                for chunk in chunker_output.chunks:
                    chunk_data = ChunkData(
                        id=str(chunk.id),
                        content=chunk.content,
                        section_title=chunk.section_title,
                        filename=chunk.filename,
                        position=chunk.position,
                        tokens=chunk.tokens,
                        type=chunk.type,
                        content_json=chunk.content_json,
                        heading_level=chunk.heading_level,
                    )
                    chunk_data_list.append(chunk_data)

                embedder_input = EmbedderInput(
                    chunks=chunk_data_list,
                    metadata=file_metadata,
                )
                embedder_output = asyncio.run(self.embedder.process(embedder_input))

                if embedder_output.index_name:
                    embeddings_created = len(chunk_data_list)
                    logger.info(f'Created {embeddings_created} embeddings and indexed to {embedder_output.index_name}')
                else:
                    embeddings_created = 0
                    logger.warning('Failed to create embeddings or index')

            except Exception as e:
                logger.error(f'Error creating embeddings: {e}')
                embeddings_created = 0
                status = 'failed'

            processing_time = time.time() - start_time
            logger.info(f'Document upload completed successfully in {processing_time:.2f}s')

            return UploadDocumentOutput(
                status=status,
                message=f'Successfully processed {processed_chunks} chunks and created {embeddings_created} embeddings',
                processed_chunks=processed_chunks,
                embeddings_created=embeddings_created,
                processing_time=processing_time,
                filename=input_data.file.filename,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f'Failed to process document: {str(e)}'
            logger.error(error_msg, exc_info=True)

            return UploadDocumentOutput(
                status='error',
                message='Document processing failed',
                processed_chunks=processed_chunks,
                embeddings_created=embeddings_created,
                processing_time=processing_time,
                error=error_msg,
                filename=input_data.file.filename,
            )

    def upload_multiple_documents(self, input_data: UploadMultipleDocumentsInput) -> UploadMultipleDocumentsOutput:
        """Upload and process multiple documents using multi-worker processing."""
        start_time = time.time()
        total_files = len(input_data.files)

        if total_files <= 1:
            # Single file processing - no need for multi-worker
            if total_files == 1:
                result = self.upload_document(UploadDocumentInput(file=input_data.files[0]))
                return UploadMultipleDocumentsOutput(
                    total_files=1,
                    successful_files=1 if result.status == 'success' else 0,
                    failed_files=0 if result.status == 'success' else 1,
                    total_chunks=result.processed_chunks,
                    total_embeddings=result.embeddings_created,
                    total_processing_time=time.time() - start_time,
                    file_results=[result],
                    errors=[result.error] if result.error else [],
                )
            else:
                return UploadMultipleDocumentsOutput(
                    total_files=0,
                    successful_files=0,
                    failed_files=0,
                    total_chunks=0,
                    total_embeddings=0,
                    total_processing_time=0,
                    file_results=[],
                    errors=['No files provided'],
                )

        # Determine number of workers using configuration
        if input_data.max_workers is not None:
            max_workers = input_data.max_workers
        else:
            max_workers = get_optimal_worker_count(total_files)

        logger.info(f'Processing {total_files} files with {max_workers} workers')

        file_results = []
        errors = []

        try:
            # Use ThreadPoolExecutor for I/O bound operations like file processing
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all files for processing
                future_to_file = {
                    executor.submit(self._process_single_file, file): file
                    for file in input_data.files
                }

                # Collect results as they complete
                for future in as_completed(future_to_file):
                    file = future_to_file[future]
                    try:
                        result = future.result()
                        file_results.append(result)

                        if result.error:
                            errors.append(f"File {file.filename}: {result.error}")

                        logger.info(f'Completed processing {file.filename}: {result.status}')

                    except Exception as e:
                        error_msg = f'Exception processing {file.filename}: {str(e)}'
                        logger.error(error_msg, exc_info=True)
                        errors.append(error_msg)

                        # Create failed result
                        failed_result = UploadDocumentOutput(
                            status='error',
                            message='Processing failed with exception',
                            processed_chunks=0,
                            embeddings_created=0,
                            processing_time=0,
                            error=error_msg,
                            filename=file.filename,
                        )
                        file_results.append(failed_result)

        except Exception as e:
            error_msg = f'Failed to initialize multi-worker processing: {str(e)}'
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)

        # Calculate summary statistics
        successful_files = sum(1 for result in file_results if result.status == 'success')
        failed_files = total_files - successful_files
        total_chunks = sum(result.processed_chunks for result in file_results)
        total_embeddings = sum(result.embeddings_created for result in file_results)
        total_processing_time = time.time() - start_time

        logger.info(f'Multi-file processing completed: {successful_files}/{total_files} successful, '
                    f'{total_chunks} chunks, {total_embeddings} embeddings in {total_processing_time:.2f}s')

        return UploadMultipleDocumentsOutput(
            total_files=total_files,
            successful_files=successful_files,
            failed_files=failed_files,
            total_chunks=total_chunks,
            total_embeddings=total_embeddings,
            total_processing_time=total_processing_time,
            file_results=file_results,
            errors=errors,
        )

    def _process_single_file(self, file: UploadFile) -> UploadDocumentOutput:
        """Process a single file - used by multi-worker processing."""
        return self.upload_document(UploadDocumentInput(file=file))

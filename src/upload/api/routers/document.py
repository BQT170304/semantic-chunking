from __future__ import annotations

from typing import List
from typing import Optional

from application.upload import UploadDocumentApplication
from application.upload import UploadDocumentInput
from application.upload import UploadMultipleDocumentsInput
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import Request
from fastapi import UploadFile
from shared.settings import Settings

router = APIRouter(tags=['documents'])
settings = Settings()


def get_upload_application(request: Request) -> UploadDocumentApplication:
    """Dependency to get the upload application instance."""
    return UploadDocumentApplication(
        settings=None,
        parser=request.app.state.parser,
        chunker=request.app.state.chunker,
        embedder=request.app.state.embedder,
    )


@router.post('/upload')
def upload_documents(
    files: List[UploadFile],
    max_workers: Optional[int] = Form(None),
    application: UploadDocumentApplication = Depends(get_upload_application),
):
    """Upload and process multiple documents with multi-worker support.

    This endpoint accepts multiple file uploads and processes them through
    the document application layer using concurrent workers when more than
    one file is provided.

    Args:
        files (List[UploadFile]): List of files to be uploaded and processed
        max_workers (Optional[int]): Maximum number of workers for concurrent processing.
                                   Defaults to min(4, number_of_files) if not specified.
        application (UploadDocumentApplication): Injected upload application instance

    Returns:
        dict: Processing results for all uploaded files with summary statistics
    """
    if not files:
        raise HTTPException(status_code=400, detail='No files provided')

    # Reset file pointers to beginning
    for file in files:
        file.file.seek(0)

    # Use multi-worker processing
    upload_input = UploadMultipleDocumentsInput(files=files, max_workers=max_workers)
    result = application.upload_multiple_documents(upload_input)

    # Format response
    return {
        'summary': {
            'total_files': result.total_files,
            'successful_files': result.successful_files,
            'failed_files': result.failed_files,
            'total_chunks_processed': result.total_chunks,
            'total_embeddings_created': result.total_embeddings,
            'total_processing_time': result.total_processing_time,
            'workers_used': max_workers or min(4, len(files)) if len(files) > 1 else 1,
        },
        'results': [
            {
                'filename': file_result.filename,
                'status': file_result.status,
                'message': file_result.message,
                'processed_chunks': file_result.processed_chunks,
                'embeddings_created': file_result.embeddings_created,
                'processing_time': file_result.processing_time,
                'error': file_result.error,
            }
            for file_result in result.file_results
        ],
        'errors': result.errors,
    }


@router.post('/upload/single')
async def upload_single_document(
    file: UploadFile,
    application: UploadDocumentApplication = Depends(get_upload_application),
):
    """Upload and process a single document.

    This endpoint is optimized for single file processing without the overhead
    of multi-worker coordination.

    Args:
        file (UploadFile): File to be uploaded and processed
        application (UploadDocumentApplication): Injected upload application instance

    Returns:
        dict: Processing result for the uploaded file
    """
    if not file:
        raise HTTPException(status_code=400, detail='No file provided')

    try:
        # Reset file pointer to beginning
        file.file.seek(0)

        # Process the file through the application
        upload_input = UploadDocumentInput(file=file)
        result = await application.upload_document(upload_input)

        return {
            'filename': result.filename,
            'status': result.status,
            'message': result.message,
            'processed_chunks': result.processed_chunks,
            'embeddings_created': result.embeddings_created,
            'processing_time': result.processing_time,
            'error': result.error,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Failed to process file {file.filename}: {str(e)}',
        )


@router.get('/get_all')
async def get_documents():
    """Retrieve all documents.

    Returns:
        Document: All documents
    """
    return {'message': 'All documents retrieved'}


@router.put('/{document_id}')
async def update_document(document_id: str):
    """Update a specific document by ID.

    Args:
        document_id (str): Unique identifier of the document to update

    Returns:
        Document: The updated document
    """
    return {'message': f'Document {document_id} updated'}


@router.delete('/{document_id}')
async def delete_document(document_id: str):
    """Delete a specific document by ID.

    Args:
        document_id (str): Unique identifier of the document to delete

    Returns:
        dict: Status message indicating successful deletion
    """
    return {'message': f'Document {document_id} deleted'}

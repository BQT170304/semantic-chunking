from __future__ import annotations

from typing import List

from application.upload import UploadDocumentApplication
from application.upload import UploadDocumentInput
from fastapi import APIRouter
from fastapi import Depends
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
    application: UploadDocumentApplication = Depends(get_upload_application),
):
    """Upload and process multiple documents.

    This endpoint accepts multiple file uploads and processes them through
    the document application layer. Each file is processed and its status
    is tracked.

    Args:
        files (List[UploadFile]): List of files to be uploaded and processed
        application (UploadDocumentApplication): Injected upload application instance

    Returns:
        dict: Processing results for all uploaded files
    """
    if not files:
        raise HTTPException(status_code=400, detail='No files provided')

    results = []

    for file in files:
        try:
            # Reset file pointer to beginning
            file.file.seek(0)

            # Process each file through the application
            upload_input = UploadDocumentInput(file=file)
            result = application.upload_document(upload_input)

            results.append({
                'filename': file.filename,
                'status': result.status,
                'message': result.message,
                'processed_chunks': result.processed_chunks,
                'embeddings_created': result.embeddings_created,
                'processing_time': result.processing_time,
                'error': result.error,
            })

        except Exception as e:
            results.append({
                'filename': file.filename,
                'status': 'error',
                'message': 'Failed to process file',
                'processed_chunks': 0,
                'embeddings_created': 0,
                'processing_time': None,
                'error': str(e),
            })

    # Calculate summary statistics
    total_chunks = sum(r['processed_chunks'] for r in results)
    total_embeddings = sum(r['embeddings_created'] for r in results)
    successful_files = sum(1 for r in results if r['status'] == 'success')

    return {
        'summary': {
            'total_files': len(files),
            'successful_files': successful_files,
            'failed_files': len(files) - successful_files,
            'total_chunks_processed': total_chunks,
            'total_embeddings_created': total_embeddings,
        },
        'results': results,
    }


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

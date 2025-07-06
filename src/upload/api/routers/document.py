from __future__ import annotations

from typing import List

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from fastapi import UploadFile
from shared.settings import Settings

router = APIRouter(tags=['documents'])
settings = Settings()


@router.post('/upload')
def upload_documents(
    request: Request,
    files: List[UploadFile],
):  # Removed application dependency
    """Upload and process multiple documents.

    This endpoint accepts multiple file uploads and processes them through
    the document application layer. Each file is processed and its status
    is tracked.

    Args:
        files (List[UploadFile]): List of files to be uploaded and processed
        application (UploadDocumentApplication): Injected upload application instance

    Returns:
        DocumentApplicationOutput: Processing results for all uploaded files
    """
    try:
        request_data = {
            'method': 'POST',
            'files': [file.filename for file in files],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error processing files: {str(e)}')
    return request_data


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

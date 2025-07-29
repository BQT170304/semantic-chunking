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
from infra.db import Conversation
from infra.db import Document
from infra.db import SessionLocal
from shared.settings import Settings
from sqlalchemy.orm import Session

router = APIRouter(tags=['documents'])
settings = Settings()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    user_id: str = Form(...),
    max_workers: Optional[int] = Form(None),
    application: UploadDocumentApplication = Depends(get_upload_application),
    db: Session = Depends(get_db),
):
    if not files:
        raise HTTPException(status_code=400, detail='No files provided')
    for file in files:
        file.file.seek(0)
    # Generate a title (for now, just use the first file's name or a static string)
    title = f"Conversation for {files[0].filename}" if files else 'Untitled Conversation'

    user_id_num = int(user_id)
    # Create conversation with empty history
    conversation = Conversation(user_id=user_id_num, title=title, history='[]')
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    # Create document records
    for file in files:
        doc = Document(conversation_id=conversation.id, name=file.filename, size=file.size)
        db.add(doc)
    db.commit()
    # Use multi-worker processing as before
    upload_input = UploadMultipleDocumentsInput(files=files, max_workers=max_workers)
    result = application.upload_multiple_documents(upload_input)
    # Format response, include conversation_id
    return {
        'conversation_id': conversation.id,
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


# get documents by conversation_id
@router.get('/documents/{conversation_id}')
def get_documents_by_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Retrieve all documents associated with a specific conversation.

    Args:
        conversation_id (int): ID of the conversation to retrieve documents for
        db (Session): Database session dependency

    Returns:
        List[Document]: List of documents associated with the conversation
    """
    documents = db.query(Document).filter(Document.conversation_id == conversation_id).all()
    return [
        {
            'id': doc.id,
            'name': doc.name,
            'size': doc.size,
        }
        for doc in documents
    ]

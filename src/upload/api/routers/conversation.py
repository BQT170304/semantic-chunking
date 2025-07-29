from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from infra.db import Conversation
from infra.db import Document
from infra.db import SessionLocal
from passlib.context import CryptContext
from sqlalchemy.orm import Session

router = APIRouter(tags=['conversation'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.get('/conversations/user/{user_id}')
def get_conversations(user_id: int, db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(Conversation.user_id == user_id).all()
    return [
        {
            'id': c.id,
            'title': c.title,
            'history': c.history,
        }
        for c in conversations
    ]


@router.get('/conversations/{conversation_id}')
def get_conversation_detail(conversation_id: int, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail='Conversation not found')
    documents = db.query(Document).filter(Document.conversation_id == conversation_id).all()
    return {
        'id': conversation.id,
        'title': conversation.title,
        'history': conversation.history,
        'documents': [
            {
                'id': doc.id,
                'name': doc.name,
                'size': doc.size,
            }
            for doc in documents
        ],
    }

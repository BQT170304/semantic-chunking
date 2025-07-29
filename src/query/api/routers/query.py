from __future__ import annotations

import json
import logging

from api.models.query import ChatRequest
from api.models.query import ChatResponse
from application.query import ChatApplication
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from infra.db import Conversation
from infra.db import SessionLocal
from sqlalchemy.orm import Session

# Dependency for FastAPI


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(tags=['chat'])


@router.post('/chat', response_model=ChatResponse)
async def chat_endpoint(request: Request, chat_request: ChatRequest, db: Session = Depends(get_db)):
    try:
        rag = request.app.state.rag
        chat_application = ChatApplication(rag=rag)
        response = await chat_application.process(chat_request)
        # Update conversation history if conversation_id is provided
        if chat_request.conversation_id:
            conversation = db.query(Conversation).filter(Conversation.id == chat_request.conversation_id).first()
            if conversation:
                # Load existing history
                try:
                    history = json.loads(conversation.history)
                except Exception:
                    history = []
                # Append user and bot messages
                history.append({'role': 'user', 'content': chat_request.message})
                history.append({'role': 'assistant', 'content': response.message})
                conversation.history = json.dumps(history)
                db.commit()
        return response
    except ValueError as e:
        logging.error(f'Validation error: {str(e)}')
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f'Internal error: {str(e)}')
        raise HTTPException(status_code=500, detail='Internal server error')

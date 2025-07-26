from __future__ import annotations

import logging

from api.models.query import ChatRequest
from api.models.query import ChatResponse
from application.query import ChatApplication
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

router = APIRouter(tags=['chat'])


@router.post('/chat', response_model=ChatResponse)
async def chat_endpoint(request: Request, chat_request: ChatRequest):
    try:
        rag = request.app.state.rag
        chat_application = ChatApplication(rag=rag)
        return await chat_application.process(chat_request)
    except ValueError as e:
        logging.error(f'Validation error: {str(e)}')
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f'Internal error: {str(e)}')
        raise HTTPException(status_code=500, detail='Internal server error')

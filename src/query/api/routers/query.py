from __future__ import annotations

import logging

from api.models.query import AskRequest
from api.models.query import AskResponse
from application.query import AskApplication
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

router = APIRouter(tags=['ask'])


@router.post('/ask', response_model=AskResponse)
async def ask_endpoint(request: Request, ask_request: AskRequest):
    try:
        rag = request.app.state.rag
        ask_application = AskApplication(rag=rag)
        return await ask_application.ask(ask_request)
    except ValueError as e:
        logging.error(f'Validation error: {str(e)}')
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f'Internal error: {str(e)}')
        raise HTTPException(status_code=500, detail='Internal server error')

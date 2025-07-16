from __future__ import annotations

import logging

from api.models.query import AskRequest
from api.models.query import AskResponse
from application.query import AskApplication
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request

router = APIRouter(tags=['ask'])


def get_ask_application():
    return AskApplication()


@router.post('/ask', response_model=AskResponse)
async def ask_endpoint(
    ask_request: AskRequest,
    ask_application: AskApplication = Depends(get_ask_application),
):
    try:
        return await ask_application.ask(ask_request)
    except ValueError as e:
        logging.error(f'Validation error: {str(e)}')
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f'Internal error: {str(e)}')
        raise HTTPException(status_code=500, detail='Internal server error')

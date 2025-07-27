"""
SSE Router for real-time processing updates.
"""
from __future__ import annotations

from fastapi import APIRouter
from fastapi import Query
from fastapi.responses import StreamingResponse

from ..shared.sse import create_sse_response
from ..shared.sse import sse_manager

router = APIRouter(prefix='/sse', tags=['sse'])


@router.get('/connect')
async def connect_sse():
    """Connect to SSE stream for real-time updates."""
    session_id = sse_manager.create_session()
    return {'session_id': session_id}


@router.get('/stream/{session_id}')
async def sse_stream(session_id: str):
    """SSE endpoint for real-time processing updates."""
    return await create_sse_response(session_id)


@router.delete('/disconnect/{session_id}')
async def disconnect_sse(session_id: str):
    """Disconnect from SSE stream."""
    sse_manager.remove_session(session_id)
    return {'message': 'Disconnected'}

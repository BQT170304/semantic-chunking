from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from api.routers.query import router as ask_router
from domain.rag import RAG
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.logging import get_logger
from shared.logging import setup_logging

setup_logging(json_logs=True)
logger = get_logger('api')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for the FastAPI application."""
    logger.info('Initializing domain services...')
    rag = RAG()
    app.state.rag = rag
    logger.info('Domain services initialized successfully')
    yield

app = FastAPI(
    title='Query (Chat) Service',
    version='1.0.0',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(ask_router)


@app.get('/')
def root():
    return {
        'status': 'running',
        'service': 'Query (Ask) Service',
        'version': '1.0.0',
    }


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8001,
        reload=True,
    )

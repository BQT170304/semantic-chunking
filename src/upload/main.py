from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from api.routers import document_router
from domain.chunker import ChunkerService
from domain.embedder import EmbedderService
from domain.parser import ParserService
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
    parser = ParserService()
    chunker = ChunkerService()
    embedder = EmbedderService()

    app.state.parser = parser
    app.state.chunker = chunker
    app.state.embedder = embedder
    logger.info('Domain services initialized successfully')
    yield

app = FastAPI(
    title='Document Upload Service',
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

app.include_router(document_router)


@app.get('/')
def root():
    return {
        'status': 'running',
        'service': 'Document Upload Service',
        'version': '1.0.0',
    }


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=True,
    )

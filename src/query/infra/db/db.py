from __future__ import annotations

import os
import urllib.parse

from shared.logging import get_logger
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

logger = get_logger(__name__)

POSTGRES_ENDPOINT = os.getenv('POSTGRES_ENDPOINT', 'localhost')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
POSTGRES_PASSWORD = urllib.parse.quote_plus(POSTGRES_PASSWORD)
POSTGRES_DB = 'semantic-chunking'
DATABASE_URL = os.getenv('DATABASE_URL', f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_ENDPOINT}:5432/{POSTGRES_DB}')

engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

try:
    with engine.connect() as connection:
        logger.info('Connected to the database successfully.')
except OperationalError as e:
    logger.error('Failed to connect to the database.')
    logger.error(f"Error details: {e}")


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), nullable=False)
    phone = Column(String(32), unique=True, nullable=False)
    password = Column(String(128), nullable=False)


class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String(256), nullable=False)
    history = Column(Text, nullable=False, default='[]')


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, nullable=False)
    name = Column(String(256), nullable=False)
    size = Column(Integer, nullable=False)


Base.metadata.create_all(bind=engine)

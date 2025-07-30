from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from infra.db import SessionLocal
from infra.db import User
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(tags=['auth'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class RegisterRequest(BaseModel):
    username: str
    phone: str
    password: str


class LoginRequest(BaseModel):
    phone: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    phone: str

    class Config:
        orm_mode = True


@router.post('/register')
def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.phone == req.phone).first()
    if existing:
        return {'error': 'Phone already registered'}
    hashed_pw = pwd_context.hash(req.password)
    user = User(username=req.username, phone=req.phone, password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(id=user.id, username=user.username, phone=user.phone)


@router.post('/login')
def login_user(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == req.phone).first()
    if not user or not pwd_context.verify(req.password, user.password):
        return {'error': 'Invalid phone or password'}
    return UserResponse(id=user.id, username=user.username, phone=user.phone)

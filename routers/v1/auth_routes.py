from fastapi import APIRouter, Depends, status, BackgroundTasks
from controllers.auth_controller import AuthController
from sqlmodel import Session
from database.db import get_session
from schema.auth_schema import LoginSchema
from middlewares.auth_middleware import JWTBearer


router = APIRouter(prefix="/auth", tags=['Auth'])

auth_controller = AuthController()


@router.post("/login")
async def login(credentials: LoginSchema, session: Session = Depends(get_session)):
    return await auth_controller.login(session, credentials)


@router.get("/me")
async def me(payload: dict = Depends(JWTBearer()), session: Session = Depends(get_session)):
    return await auth_controller.me(session, payload)

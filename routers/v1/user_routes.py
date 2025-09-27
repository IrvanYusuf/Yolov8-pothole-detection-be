from fastapi import APIRouter, Depends, status
from controllers.user_controller import UserController
from sqlmodel import Session
from database.db import get_session
from schema.user_schema import UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=['Users'])

user_controller = UserController()


@router.get("/")
async def index(session: Session = Depends(get_session)):
    return await user_controller.index(session)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def store(user: UserCreate, session: Session = Depends(get_session)):
    return await user_controller.store(session, user)


@router.get("/{id}")
async def show(id: str, session: Session = Depends(get_session)):
    return await user_controller.show(session, id)


@router.patch("/{id}")
async def update(id: str, user_update: UserUpdate, session: Session = Depends(get_session)):
    return await user_controller.update(session, id, user_update)


@router.delete("/{id}")
async def destroy(id: str, session: Session = Depends(get_session)):
    return await user_controller.destroy(session, id)

from sqlmodel import Session, select
from models.models import User
from schema.user_schema import UserCreate, UserSchema, UserUpdate
from utils.utils import generate_password, check_valid_uuid
from fastapi import HTTPException, status


class UserController():

    @staticmethod
    async def index(session: Session):
        statement = select(User)
        users = session.exec(statement=statement).all()
        return {"message": "success get user", "data": users}

    @staticmethod
    async def store(session: Session, user: UserCreate):
        new_user = User(**user.model_dump())
        password, hashed = generate_password()
        new_user.password = hashed
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        user_dict = new_user.model_dump()
        user_dict["password"] = password
        return {"message": "success create new user", "data": user_dict}

    @staticmethod
    async def show(session: Session, id: str) -> UserSchema:
        valid_uuid = check_valid_uuid(id)
        user = session.get(User, valid_uuid)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                                "message": "User not found"})
        user_dict = user.model_dump()
        user_dict.pop("password", None)
        return {"message": "success get user detail", "data": user_dict}

    @staticmethod
    async def update(session: Session, id: str, user_update: UserUpdate):
        valid_uuid = check_valid_uuid(id)
        user = session.get(User, valid_uuid)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                                "message": "User not found"})

        # Apply only provided fields
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        session.add(user)
        session.commit()
        session.refresh(user)

        user_dict = user.model_dump()
        user_dict.pop("password", None)
        return {"message": "success update user", "data": user_dict}

    @staticmethod
    async def destroy(session: Session, id: str):
        valid_uuid = check_valid_uuid(id)
        deleted_user = session.get(User, valid_uuid)
        if not deleted_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                                "message": "User not found"})

        session.delete(deleted_user)
        session.commit()
        return {"message": "success deleted user", "data": {}}

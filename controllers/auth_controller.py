from schema.auth_schema import AuthSchema, LoginSchema
from sqlmodel import Session, select
from models.models import User
from fastapi import HTTPException, status, Depends
from middlewares.auth_middleware import JWTBearer
from lib.password_hash import Hasher
from utils.utils import check_valid_uuid
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import jwt


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


class AuthController:
    @staticmethod
    async def login(session: Session, credentials: LoginSchema):
        statement = select(User).where(User.email == credentials.email)
        user = session.exec(statement).first()

        if not user or not Hasher.verify_password(credentials.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email atau password salah"
            )

        token_data = {"sub": str(user.id)}
        access_token = AuthController.create_access_token(token_data)
        user_data = user.model_dump()
        user_data.pop("password", None)

        payload = AuthSchema(user=user_data, token={
                             "access_token": access_token, "token_type": "bearer"})

        return {
            "message": "success login",
            "data": payload
        }

    @staticmethod
    async def me(session: Session, payload: dict = Depends(JWTBearer())):
        user_id = check_valid_uuid(payload.get("sub"))
        user = session.get(User, user_id)
        user_data = user.model_dump()
        user_data.pop("password", None)

        return {
            "message": "success get user",
            "data": user_data
        }

    def create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

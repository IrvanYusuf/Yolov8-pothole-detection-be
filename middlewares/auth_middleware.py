from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials and credentials.scheme == "Bearer":
            payload = self.decode_jwt(credentials.credentials)
            if not payload:
                raise HTTPException(
                    status_code=401, detail="Invalid or expired token")
            return payload
        raise HTTPException(status_code=401, detail="Unauthorized")

    def decode_jwt(self, token: str):
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.PyJWTError:
            return None

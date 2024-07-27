from collections.abc import Generator
from typing import Annotated, Tuple

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine
from app.core import security
from app.models import User, UserInDB, TokenPayload


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request, session: SessionDep):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme.")
            is_valid, token_data = self.verify_jwt(credentials.credentials)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token or expired token.")
            user = session.get(UserInDB, token_data.sub)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return User(**user.model_dump())
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> Tuple[bool, TokenPayload]:
        isTokenValid: bool = False

        try:
            payload = security.decode_jwt(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True

        return isTokenValid, TokenPayload(**payload)


AuthUser = Annotated[User, Depends(JWTBearer())]

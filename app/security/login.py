from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import jwt

from datetime import datetime, timezone, timedelta
from typing import Annotated

from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class JWTManager:
    def create_access_token(self, user_id: int) -> str:
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "type": "access",
        }

        return jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)

    def get_id_by_access_token(self, token: Annotated[str, oauth2_scheme]):
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )

            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="invalid token type",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            user_id = payload.get("sub")

            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="the token does not contain an ID",
                )

            return user_id

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="the token is invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )


TokenManager = JWTManager()

GetId = Annotated[str, Depends(TokenManager.get_id_by_access_token)]

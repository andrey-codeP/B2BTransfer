from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import hashlib
import uuid
import jwt

from datetime import datetime, timezone, timedelta
from typing import Annotated

from app.exceptions.token_exception import InvalidTokenError
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class JWTManager:
    @staticmethod
    def hash_token(token: str) -> str:
        """хешируем токен для хранения в бд"""
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def create_access_token(user_id: int) -> str:
        """создаем аксес токен"""
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "type": "access",
            "jti": str(uuid.uuid4()),
        }

        return jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """создаем рефреш токен"""
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc)
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            "type": "refresh",
            "jti": str(uuid.uuid4()),
        }

        return jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)

    @staticmethod
    def decode_token(token: str, expected_type: str) -> int:
        """декодирует токен, проверяет тип и возвращает user_id"""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            if payload.get("type") != expected_type:
                raise InvalidTokenError()

            user_id = payload.get("sub")
            if user_id is None:
                raise InvalidTokenError()

            return int(user_id)
        except jwt.PyJWTError:
            raise InvalidTokenError()

    @classmethod
    def get_id_by_access_token(
        cls, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> int:
        """зависимость для защищенных эндпоинтов"""
        try:
            return cls.decode_token(token, expected_type="access")
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token",
                headers={"WWW-Authenticate": "Bearer"},
            )


TokenManager = JWTManager()

GetId = Annotated[int, Depends(TokenManager.get_id_by_access_token)]

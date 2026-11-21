from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi import APIRouter, status, Depends, Response, Cookie, HTTPException

from typing import Annotated

from app.exceptions.token_exception import InvalidTokenError
from app.database.dependencies.services_dep import UserServiceDep, LoginServiceDep
from app.security.login import TokenManager
from app.schemas.user import SUserResponse, SUserCreate
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/registry", status_code=status.HTTP_201_CREATED, response_model=SUserResponse
)
async def registry_user(user_service: UserServiceDep, user_data: SUserCreate):
    """регистрируем юзера"""
    user = await user_service.create_user(user_data)
    return user


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(
    login_service: LoginServiceDep,
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
) -> dict:
    """выдаем аксес токен в заголовке и рефреш токен в куках"""
    tokens = await login_service.login(user_data.username, user_data.password)
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # запрещает доступ через JavaScript, защита от XSS
        secure=True,  # кука передается только по HTTPS (защита от перехвата)
        samesite="lax",  # запрещает отправку куки с чужих сайтов при POST (защита от CSRF)
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",  # кука доступна для всех путей на домене
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_access_token(
    response: Response,
    login_service: LoginServiceDep,
    refresh_token: Annotated[str | None, Cookie()] = None,  # <--- берем саму куку
) -> dict | JSONResponse:
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="refresh token missing",
        )

    try:
        tokens = await login_service.refresh(refresh_token)
    except InvalidTokenError:
        err_response = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid or expired token"},
        )
        err_response.delete_cookie(
            key="refresh_token",
            httponly=True,
            secure=True,
            samesite="lax",
            path="/",
        )
        return err_response

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )

    return {"access_token": tokens["access_token"], "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    response: Response,
    login_service: LoginServiceDep,
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    """Выход из аккаунта: удаляем токен из БД и чистим куку"""
    await login_service.logout(refresh_token)
    response.delete_cookie(
        key="refresh_token", httponly=True, secure=True, samesite="lax", path="/"
    )

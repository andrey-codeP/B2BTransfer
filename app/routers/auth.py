from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, status, Depends, Response, Cookie

from typing import Annotated

from app.database.dependencies.services_dep import UserServiceDep, LoginServiceDep
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

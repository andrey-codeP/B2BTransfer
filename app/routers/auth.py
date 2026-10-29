from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, status, Depends

from typing import Annotated

from app.database.dependencies.services_dep import UserServiceDep, LoginServiceDep
from app.schemas.user import SUserResponse, SUserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/registry", status_code=status.HTTP_201_CREATED, response_model=SUserResponse
)
async def registry_user(user_service: UserServiceDep, user_data: SUserCreate):
    user = await user_service.create_user(user_data)
    return user


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(
    login_service: LoginServiceDep,
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    access_token = await login_service.login(user_data.username, user_data.password)
    return {"access_token": access_token, "token_type": "bearer"}

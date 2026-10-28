from fastapi import APIRouter, status

from app.database.depends import UserServiceDep
from app.schemas.user import SUserResponse, SUserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registry", status_code=status.HTTP_201_CREATED)
async def registry_user(
    user_service: UserServiceDep, user_data: SUserCreate
) -> SUserResponse:
    user = await user_service.create_user(user_data)
    return user
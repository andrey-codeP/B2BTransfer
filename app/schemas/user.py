from pydantic import BaseModel, ConfigDict


class SUser(BaseModel):
    """для соблюдения DRY"""
    username: str


class SUserCreate(SUser):
    """валидируем то что принимаем от юзера для создания его в бд"""
    password: str


class SUserResponse(SUser):
    """валидируем то что выдаем юзеру в ответ"""
    id: int


class SUserInDb(SUser):
    """валидация того, что мы возращаем из репозитория"""
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)

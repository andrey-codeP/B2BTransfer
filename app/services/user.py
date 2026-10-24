
from app.database.models import UserTable
from app.security import password_manager
from app.exceptions.user_exception import UsernameAlreadyExistsError
from app.schemas.user import SUserCreate, SUserResponse
from app.database.uow import UnitOfWork

class UserServices:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def create_user(self, user_data: SUserCreate) -> SUserResponse:
        async with self.uow as uow:
            existing = await uow.user_rep.get_user_by_username(user_data.username)
            if existing:
                raise UsernameAlreadyExistsError()

            hashed_password = password_manager.create_hash_password(SUserCreate.password)

            user = UserTable(
               username=SUserCreate.username,
               hashed_password=hashed_password
            )

           await uow.user_rep.create_user(user)

        return SUserResponse.model_validate(user)


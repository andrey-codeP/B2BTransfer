from app.exceptions.base_exceptions import AppException


class UsernameAlreadyExistsError(AppException):
    """ошибка если пользователь уже есть в бд"""

    status_code: int = 409
    error_code: str = "username_already_exists"
    message: str = "Username already exists"

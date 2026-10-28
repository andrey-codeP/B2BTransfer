from app.exceptions.base_exceptions import AppException


class UsernameAlreadyExistsError(AppException):
    """ошибка если пользователь уже есть в бд"""

    status_code: int = 409
    error_code: str = "username_already_exists"
    message: str = "Username already exists"


class UserNotFoundError(AppException):
    """ошибка если пользователь не найден"""

    status_code = 404
    error_code = "user_not_found"
    message = "User not found"


class IncorrectPasswordError(AppException):
    status_code = 401
    error_code = "incorrect_password"
    message = "Incorrect password"

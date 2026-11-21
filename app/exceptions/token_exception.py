from app.exceptions.base_exceptions import AppException


class InvalidTokenError(AppException):
    """ошибка для невалидного или просроченного токена"""

    status_code = 401
    error_code = "invalid_token"
    message = "Invalid or expired token"

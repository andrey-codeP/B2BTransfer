from app.exceptions.base_exceptions import AppException


class WalletAlreadyExistsError(AppException):
    """ошибка если кошелек уже есть"""

    status_code: int = 409
    error_code: str = "wallet_already_exists"
    message: str = "wallet already exists"


class WalletNotFoundError(AppException):
    """ошибка если кошелек не найден"""

    status_code = 404
    error_code = "wallet_not_found"
    message = "wallet not found"

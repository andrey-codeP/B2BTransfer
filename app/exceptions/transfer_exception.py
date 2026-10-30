from app.exceptions.base_exceptions import AppException


class InsufficientFundsError(AppException):
    """ошибка если средств недостаточно"""

    status_code: int = 402
    error_code: str = "insufficient_funds"
    message: str = "insufficient Funds"


class SelfTransferError(AppException):
    """ошикба если перевод был самому себе"""

    status_code: int = 402
    error_code: str = "self_transfer"
    message: str = "self transfer"

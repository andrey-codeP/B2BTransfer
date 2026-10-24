from abc import ABC, abstractmethod


class AppError(ABC):
    """абстракция для ошибок"""

    status_code: int
    error_code: str
    message: str

    @abstractmethod
    def to_dict(self) -> dict:
        pass


class AppException(AppError, Exception):
    """общий тип для всех ошибок"""

    def to_dict(self) -> dict:
        return {
            "error_code": self.error_code,
            "message": self.message,
        }

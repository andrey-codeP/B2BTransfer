from abc import ABC, abstractmethod


class AppError(ABC):
    """Абстракция для ошибок приложения"""

    status_code: int = 500
    error_code: str = "internal_error"
    message: str = "An internal error occurred"

    @abstractmethod
    def to_dict(self) -> dict:
        """Метод для сериализации ошибки в ответ для клиента"""
        pass


class AppException(Exception, AppError):
    """Общий базовый класс для всех кастомных исключений проекта"""

    def __init__(self, message: str | None = None):
        self.message = message or self.message
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "error_code": self.error_code,
            "message": self.message,
        }

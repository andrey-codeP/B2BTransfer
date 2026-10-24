from abc import ABC, abstractmethod

class AppError(ABC):
    status_code: int
    error_code: str
    message: str

    @abstractmethod
    def to_dict(self) -> dict:
        pass


class AppException(AppError, Exception):
    def to_dict(self) -> dict:
        return {
            "error_code": self.error_code,
            "message": self.message,
        }
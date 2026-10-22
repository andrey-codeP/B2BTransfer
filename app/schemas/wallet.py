from pydantic import BaseModel, ConfigDict

from decimal import Decimal


class SWalletBase(BaseModel):
    """позволяем обращаться ко
    всем наследникамкак к орм модели"""

    model_config = ConfigDict(from_attributes=True)


class SWalletCreate(SWalletBase):
    """валидируем то что присылает юзер
    для создания кошелька, но счет по умолчанию
    равен 0.00"""

    user_id: int
    balance: Decimal = Decimal("0.00")


class SWalletResponse(SWalletBase):
    """валидируем ответ пользователю"""

    id: int
    user_id: int
    balance: Decimal
    is_active: bool

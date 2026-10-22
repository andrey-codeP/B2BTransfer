from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal


class STransferBase(BaseModel):
    """соблюдаем DRY наследуя все классы
    не от BaseModel, а от базы"""

    pass


class STransferCreate(STransferBase):
    """валидируем то, что юзер присылает нам из вне
    для создания трансфера в бд"""

    amount: Decimal = Field(gt=Decimal("0"))
    from_wallet_id: int
    to_wallet_id: int


class STransferResponse(STransferBase):
    """валидируем то, какую информацию
    о трансфере мы отдаем юзеру"""

    id: int
    amount: Decimal = Field(gt=Decimal("0"))
    from_wallet_id: int
    to_wallet_id: int

    model_config = ConfigDict(from_attributes=True)

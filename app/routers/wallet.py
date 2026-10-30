from fastapi import APIRouter, status, Response

from app.database.dependencies.services_dep import WalletServiceDep
from app.schemas.wallet import SWalletResponse
from app.security.login import GetId

router = APIRouter(
    prefix="/wallet",
    tags=["wallet"],
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SWalletResponse)
async def create_wallet(user_id: GetId, wallet_service: WalletServiceDep):
    wallet = await wallet_service.create_wallet_by_user_id(user_id=user_id)
    return SWalletResponse.model_validate(wallet)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_by_user_id(
    user_id: GetId, wallet_service: WalletServiceDep
) -> Response:
    wallet = await wallet_service.get_wallet_user_id(user_id=user_id)
    wallet_id = wallet.id

    await wallet_service.delete_wallet(wallet_id=wallet_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

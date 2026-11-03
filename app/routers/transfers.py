from fastapi import APIRouter, status, Response, BackgroundTasks

from app.background_tasks.log_transfer_task import log_transfer_action
from app.logger_manager import transfer_logger
from app.schemas.transfers import STransferCreate
from app.security.login import GetId
from app.database.dependencies.services_dep import TransferServiceDep

router = APIRouter(
    prefix="/transfers",
    tags=["transfers"],
)


@router.post("/transfer", status_code=status.HTTP_201_CREATED)
async def create_transfer(
    transfer_service: TransferServiceDep,
    sender_user_id: GetId,
    transfer_data: STransferCreate,
    background_tasks: BackgroundTasks
):
    transfer_logger.info(
        f"Получен запрос на транзакцию от {sender_user_id} к {transfer_data.recipient_user_id}"
    )

    await transfer_service.create_transfer(
        sender_user_id=sender_user_id,
        recipient_user_id=transfer_data.recipient_user_id,
        amount=transfer_data.amount,
    )

    background_tasks.add_task(
        log_transfer_action,
        sender_id=sender_user_id,
        recipient_id=transfer_data.recipient_user_id,
        amount=transfer_data.amount
    )
    return Response(status_code=status.HTTP_201_CREATED)

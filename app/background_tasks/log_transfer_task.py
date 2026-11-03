from decimal import Decimal

from app.logger_manager import transfer_logger


def log_transfer_action(
    sender_id: int, recipient_id: int, amount: Decimal
) -> None:
    try:
        transfer_logger.info(
            f"--> успешный перевод "
            f"отправитель {sender_id} -> Получатель {recipient_id}, "
            f"сумма: {amount} <--"
        )
    except Exception as e:
        transfer_logger.error(f"Ошибка при логировании трансфера: {e}")

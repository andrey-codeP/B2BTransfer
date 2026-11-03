from fastapi import Request

from time import perf_counter

from app.logger_manager import global_logger


async def middleware_for_log(request: Request, call_next):
    start_time = perf_counter()

    global_logger.info(f"--> Был вызван метод {request.method} на {request.url.path}")

    try:
        response = await call_next(request)

        finally_time_ms = (perf_counter() - start_time) * 1000

        global_logger.info(
            f"<-- Запрос {request.method} на {request.url.path} "
            f"завершился со статус кодом: {response.status_code} "
            f"за {finally_time_ms:.2f} мс"
        )
        return response

    except Exception as e:
        finally_time_ms = (perf_counter() - start_time) * 1000

        global_logger.error(
            f"X-- Запрос {request.method} на {request.url.path} "
            f"упал с ошибкой за {finally_time_ms:.2f} мс"
        )
        raise e

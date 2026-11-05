from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.middlewares.global_log import middleware_for_log
from app.routers.auth import router as auth_router
from app.routers.wallet import router as wallet_router
from app.routers.transfers import router as transfer_router
from app.exceptions.base_exceptions import AppException
from app.logger_manager import exceptions_logger

app = FastAPI(
    title="B2B Transfer",
    description="B2B Transfer",
    version="1.0.0",
)


app.middleware("http")(middleware_for_log)

app.include_router(auth_router)
app.include_router(wallet_router)
app.include_router(transfer_router)


@app.exception_handler(AppException)
async def exceptions_handler(request: Request, exc: AppException):
    """логируем а так же отлавлвиаем исключения"""
    error_log_text = (
        f"исключение {exc.__class__.__name__} "
        f"при запросе {request.url.path} {request.method}\n"
        f"детали ошибки: {exc.to_dict()}\n"
        f"с статус кодом {exc.status_code}"
    )
    exceptions_logger.exception(error_log_text)
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

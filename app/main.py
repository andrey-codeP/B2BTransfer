from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routers.auth import router as auth_router
from app.routers.wallet import router as wallet_router
from app.routers.transfers import router as transfer_router
from app.exceptions.base_exceptions import AppException

app = FastAPI(
    title="B2B Transfer",
    description="B2B Transfer",
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(wallet_router)
app.include_router(transfer_router)


@app.exception_handler(AppException)
async def exceptions_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )
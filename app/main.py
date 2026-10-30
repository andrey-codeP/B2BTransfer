from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.wallet import router as wallet_router
from app.routers.transfers import router as transfer_router

app = FastAPI(
    title="B2B Transfer",
    description="B2B Transfer",
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(wallet_router)
app.include_router(transfer_router)

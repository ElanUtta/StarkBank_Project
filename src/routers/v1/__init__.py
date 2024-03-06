from src.routers.v1.webhook import webhook_router
from fastapi import APIRouter

sub_router = APIRouter(
    prefix="/v1",
    tags=["v1"],
)

sub_router.include_router(webhook_router)

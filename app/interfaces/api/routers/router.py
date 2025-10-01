
from fastapi import APIRouter
from app.interfaces.api.controllers.healthy_controller import router as healthy_router

def create_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(healthy_router)
    return router
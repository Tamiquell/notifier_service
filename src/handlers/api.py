from fastapi import APIRouter
from src.handlers import notify

router = APIRouter()
router.include_router(notify.router)

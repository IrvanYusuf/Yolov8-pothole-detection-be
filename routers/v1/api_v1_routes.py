from fastapi import APIRouter
from . import user_routes

router = APIRouter()

router.include_router(user_routes.router)

from fastapi import APIRouter
from .v1 import api_v1_routes

router = APIRouter()


router.include_router(api_v1_routes.router, prefix="/v1")

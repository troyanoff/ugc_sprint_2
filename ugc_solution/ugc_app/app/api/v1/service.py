from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.service_functions import security_jwt

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def perform_healthcheck() -> JSONResponse:
    """
    Healthcheck endpoint
    """
    return JSONResponse(content={"status": "UP"})


@router.get("/health_w_auth", status_code=status.HTTP_200_OK)
async def perform_healthcheck_w_auth(
    user: Annotated[dict, Depends(security_jwt)]
) -> JSONResponse:
    """
    Healthcheck endpoint
    """
    return JSONResponse(content={"status": "UP", "user": user})

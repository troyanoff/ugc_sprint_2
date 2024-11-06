from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from src.services.auth import get_jwt_with_roles, security_jwt

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


@router.get("/health_w_auth_and_role", status_code=status.HTTP_200_OK)
async def perform_healthcheck_w_auth_and_role(
    user: Annotated[dict, Depends(get_jwt_with_roles(["Admin"]))]
) -> JSONResponse:
    """
    Healthcheck endpoint
    """
    return JSONResponse(content={"status": "UP", "user": user})

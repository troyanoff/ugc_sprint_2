import http
import time
from typing import List, Optional

import aiohttp
import jwt
from aiohttp.client_exceptions import ClientConnectionError
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from redis.exceptions import ConnectionError
from src.core.config import settings
from src.core.logger import logger
from src.db.redis_db import get_redis


class TokenData(BaseModel):
    sub: str
    role: List[str]
    ip_address: str
    user_agent: str


class AccessTokenEncripted(BaseModel):
    token: str


def decode_token(token: str) -> Optional[dict]:
    try:
        decoded_token = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return decoded_token if decoded_token["exp"] >= time.time() else None
    except Exception:
        return None


async def verify_user_data(token: str) -> bool:
    url = f"http://{settings.auth_service_host}:{settings.auth_service_port}/api/v1/users/check_access_token"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, json=AccessTokenEncripted(token=token).model_dump()
        ) as response:
            if response.status == 200:
                user_data = await response.json()
                if user_data is True:
                    return True

    return False


async def is_blacklisted(token: str) -> Optional[bool]:
    redis = await get_redis()
    exists = await redis.exists(token)
    if exists == 1:
        return True
    return False


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid authorization code.",
            )
        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail="Only Bearer token might be accepted.",
            )

        is_auth_verified_token = await self.verify_token(credentials.credentials)
        if is_auth_verified_token is False:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid or expired token.",
            )

        if is_auth_verified_token is None:
            is_blacklisted_token = await self.check_black_list(credentials.credentials)
            if is_blacklisted_token is True:
                raise HTTPException(
                    status_code=http.HTTPStatus.FORBIDDEN, detail="Blacklisted token."
                )

        decoded_token = self.parse_token(credentials.credentials)
        if not decoded_token:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid or expired token.",
            )

        return decoded_token

    async def verify_token(self, token: str) -> Optional[bool]:
        try:
            return await verify_user_data(token)
        except ClientConnectionError:
            logger.warning(
                "FastAPISolution - Unable to verify with auth service, continuing without verification."
            )
            return None

    async def check_black_list(self, token: str) -> Optional[bool]:
        try:
            return await is_blacklisted(token)
        except ConnectionError:
            logger.warning(
                "FastAPISolution - Unable to check blacklist, continuing without checking."
            )
            return None

    @staticmethod
    def parse_token(jwt_token: str) -> Optional[dict]:
        return decode_token(jwt_token)


class JWTBearerWithRoles(JWTBearer):
    def __init__(self, roles: List[str], auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.roles = roles

    async def __call__(self, request: Request) -> dict:
        decoded_token = await super().__call__(request)
        if not self.check_roles(decoded_token["role"]):
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="You do not have the necessary permissions to access this resource.",
            )
        return decoded_token

    def check_roles(self, user_roles: List[str]) -> bool:
        return any(role in user_roles for role in self.roles)


if settings.auth_check_is_on:
    security_jwt = JWTBearer()

    # Define a dependency that checks for specific roles
    def get_jwt_with_roles(roles: list):
        return JWTBearerWithRoles(roles=roles)

else:
    security_jwt = lambda: {}  # type: ignore

    def get_jwt_with_roles(roles: list):
        return lambda: {}

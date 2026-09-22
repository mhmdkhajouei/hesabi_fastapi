from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies import get_auth_service, get_user_service
from app.schemas import (
    Token,
    TokenRefreshRequest,
    TokenRefreshResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.service import AuthService, UserService

router = APIRouter()


@router.post(
    "/register",
    summary="Register a new user",
    description="Register a new user account with email, name, and strong password.",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user: UserRegister,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    return await service.user_register(user)


@router.post(
    "/login",
    summary="Login user",
    description="Authenticate user with email and password to receive access and refresh tokens.",
    status_code=status.HTTP_200_OK,
)
async def login(
    credentials: UserLogin,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    return await service.authenticate_user(credentials)


@router.post(
    "/refresh",
    summary="Refresh access token",
    description="Issue a new access token using a valid refresh token.",
    status_code=status.HTTP_200_OK,
)
async def refresh(
    token: TokenRefreshRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenRefreshResponse:
    return await service.request_refresh_token(token)

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.dependencies import get_user_service
from app.schemas import UserRegister, UserLogin, UserResponse, Token, TokenRefreshRequest. TokenRefreshResponse
from app.service import UserService

router = APIRouter()


@router.post(
    "/register",
    summary="Register a new user",
    description="Register a new user account with email, name, and strong password.",
    status_code=status.HTTP_201_CREATED,
    )
async def register(
    user:  UserRegister,
    service: Annotated[UserService, Depends[get_user_service]],
) -> UserResponse:
    return await service.user_register(user)

@router.post(
    "/login",
    summary="",
    description="",
    status_code=status.HTTP_200_OK,
) 
async def login(
    credentials: UserLogin,
    service: Annotated[UserService, Depends[get_user_service]],
) -> Token:
    return await service.authenticate_user(credentials)

@router.post(
    "/refresh",
    summary="",
    description="",
    status_code=status.HTTP_200_OK,
)
async def refresh(
    token: TokenRefreshRequest,
    service: Annotated[UserService, Depends[get_user_service]],
) -> TokenRefreshResponse:
    return await service.request_refresh_token(token)


    
    

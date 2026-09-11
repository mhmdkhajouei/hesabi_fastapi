from fastapi import APIRouter, status

from app.dependencies import CurrentUser
from app.schemas import UserResponse

router = APIRouter()


@router.get(
    "/me",
    summary="Get current user profile",
    description="Retrieve profile details of the authenticated and active user via Bearer token.",
    status_code=status.HTTP_200_OK,
)
async def get_me(
    current_user: CurrentUser,
) -> UserResponse:
    return UserResponse.model_validate(current_user)

from fastapi import APIRouter, Depends, status
from sqlalchemy.util.typing import Annotated

from app.dependencies import CurrentUser, get_household_service
from app.schemas import UserResponse
from app.service import HouseholdService

router = APIRouter()


@router.get(
    "/me",
    summary="Get current user profile",
    description="Retrieve profile details of the authenticated and active user via Bearer token.",
    status_code=status.HTTP_200_OK,
)
async def get_me(
    current_user: CurrentUser,
    service: Annotated[HouseholdService, Depends(get_household_service)],
) -> UserResponse:

    personal_hh_id = await service.get_personal_household_id(current_user.id)
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        personal_household_id=personal_hh_id,
    )

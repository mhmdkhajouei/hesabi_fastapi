from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.db.database import HouseholdRole
from app.dependencies import (
    HouseholdAuth,
    RequireRole,
    get_recurring_transaction_service,
)
from app.schemas import (
    RecurringTransactionResponse,
    RecurringTransactionUpdate,
)
from app.service import RecurringTransactionService

router = APIRouter()


@router.get(
    "/",
    summary="List all recurring templates",
    description="Fetch an ordered list of all recurring transaction templates for a household. All members can view this list.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RequireRole())],
)
async def get_all_templates(
    household_id: Annotated[int, Path(gt=0)],
    service: Annotated[
        RecurringTransactionService, Depends(get_recurring_transaction_service)
    ],
) -> list[RecurringTransactionResponse]:
    return await service.get_all_templates(household_id)


@router.patch(
    "/{template_id}",
    summary="Edit a recurring template",
    description="Partially update an existing recurring template. Only the household owner can perform this action.",
    status_code=status.HTTP_200_OK,
)
async def update_template(
    household_id: Annotated[int, Path(gt=0)],
    template_id: Annotated[int, Path(gt=0)],
    auth: Annotated[HouseholdAuth, Depends(RequireRole(HouseholdRole.OWNER))],
    data: RecurringTransactionUpdate,
    service: Annotated[
        RecurringTransactionService, Depends(get_recurring_transaction_service)
    ],
) -> RecurringTransactionResponse:
    return await service.update_template(
        household_id,
        template_id,
        auth.user_id,
        auth.role,
        data,
    )


@router.delete(
    "/{template_id}",
    summary="Delete a recurring template",
    description="Permanently remove a recurring template by its unique ID. Only the household owner can perform this action.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_template(
    household_id: Annotated[int, Path(gt=0)],
    template_id: Annotated[int, Path(gt=0)],
    auth: Annotated[HouseholdAuth, Depends(RequireRole(HouseholdRole.OWNER))],
    service: Annotated[
        RecurringTransactionService, Depends(get_recurring_transaction_service)
    ],
) -> None:
    await service.delete_template(
        household_id,
        template_id,
        auth.user_id,
        auth.role,
    )

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.dependencies import RequireRole, get_compute_service
from app.schemas import CategoryBalanceResponse, FinancialSummaryResponse
from app.service import ComputeService

router = APIRouter()


@router.get(
    "/summary",
    summary="Get overall financial summary",
    description="Aggregate all transactions to calculate total income, total expenses, and net balance.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RequireRole())],
)
async def get_summary(
    household_id: Annotated[int, Path(gt=0)],
    service: Annotated[ComputeService, Depends(get_compute_service)],
) -> FinancialSummaryResponse:
    result = await service.get_financial_summary(household_id)
    return FinancialSummaryResponse(**result)


@router.get(
    "/categories",
    summary="Get all categories",
    description="Calculate budget utilization, total expenses, and remaining limits across all categories.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RequireRole())],
)
async def get_all_categories(
    household_id: Annotated[int, Path(gt=0)],
    service: Annotated[ComputeService, Depends(get_compute_service)],
) -> list[CategoryBalanceResponse]:
    data = await service.categories_balance(household_id)
    return [CategoryBalanceResponse(**item) for item in data]


@router.get(
    "/{category_id}",
    summary="Get a single category",
    description="Compute the spending progress and remaining budget for a specific category by ID.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RequireRole())],
)
async def get_category(
    household_id: Annotated[int, Path(gt=0)],
    category_id: Annotated[int, Path(gt=0)],
    service: Annotated[ComputeService, Depends(get_compute_service)],
) -> CategoryBalanceResponse:
    result = await service.category_balance(household_id, category_id)
    return CategoryBalanceResponse(**result)

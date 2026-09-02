from typing import Annotated

from app.dependencies import get_compute_service
from app.schemas import CategoryBalanceResponse, FinancialSummaryResponse
from app.service import ComputeService
from fastapi import APIRouter, Depends, Path, status

router = APIRouter()


@router.get(
    "/summary",
    summary="Get overall financial summary",
    status_code=status.HTTP_200_OK,
)
async def get_summary(
    service: Annotated[ComputeService, Depends(get_compute_service)],
) -> FinancialSummaryResponse:
    result = await service.get_financial_summary()
    return FinancialSummaryResponse(**result)


@router.get(
    "/categories",
    summary="Get all categories",
    status_code=status.HTTP_200_OK,
)
async def get_all_categories(
    service: Annotated[ComputeService, Depends(get_compute_service)],
) -> list[CategoryBalanceResponse]:
    data = await service.categories_balance()
    return [CategoryBalanceResponse(**item) for item in data]


@router.get(
    "/{category_id}",
    summary="Get a single category",
    status_code=status.HTTP_200_OK,
)
async def get_category(
    category_id: Annotated[int, Path(gt=0)],
    service: Annotated[ComputeService, Depends(get_compute_service)],
) -> CategoryBalanceResponse:
    result = await service.category_balance(category_id)
    return CategoryBalanceResponse(**result)

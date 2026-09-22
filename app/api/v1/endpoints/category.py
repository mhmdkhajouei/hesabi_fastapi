from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.db.database import HouseholdRole
from app.dependencies import RequireRole, get_category_service
from app.schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from app.service import CategoryService

router = APIRouter()


@router.get(
    "/{category_id}",
    summary="Get single category",
    description="Retrieve specific category details and its budget goal by ID.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RequireRole())],
)
async def get_category(
    household_id: Annotated[int, Path(gt=0)],
    category_id: Annotated[int, Path(gt=0)],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryResponse:
    return await service.get_category(household_id, category_id)


@router.get(
    "/",
    summary="List of all categories",
    description="Fetch a list of all expense and budget categories.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RequireRole())],
)
async def get_all_categories(
    household_id: Annotated[int, Path(gt=0)],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> list[CategoryResponse]:
    return await service.get_all_categories(household_id)


@router.post(
    "/",
    summary="Create category",
    description="Create a new category alongside its assigned budget goal.",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequireRole(HouseholdRole.OWNER))],
)
async def create_category(
    household_id: Annotated[int, Path(gt=0)],
    data: CategoryCreate,
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryResponse:
    return await service.add_category(household_id, data)


@router.patch(
    "/{category_id}",
    summary="Edit a category",
    description="Partially update a category name or its budget goal. Only provided fields are updated.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RequireRole(HouseholdRole.OWNER))],
)
async def edit_category(
    household_id: Annotated[int, Path(gt=0)],
    category_id: Annotated[int, Path(gt=0)],
    data: CategoryUpdate,
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryResponse:
    return await service.edit_category(household_id, category_id, data)


@router.delete(
    "/{category_id}",
    summary="Delete a category",
    description="Permanently delete a category and its associated budget from the database.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RequireRole(HouseholdRole.OWNER))],
)
async def delete_category(
    household_id: Annotated[int, Path(gt=0)],
    category_id: Annotated[int, Path(gt=0)],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> None:
    await service.delete_category(household_id, category_id)

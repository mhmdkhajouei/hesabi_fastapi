from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.dependencies import get_category_service
from app.schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from app.service import CategoryService

router = APIRouter()


@router.get(
    "/{category_id}",
    summary="Get single category",
    description="Retrieve specific category details and its budget goal by ID.",
    status_code=status.HTTP_200_OK,
)
async def get_category(
    category_id: Annotated[int, Path(gt=0)],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryResponse:
    return await service.get_category(category_id)


@router.get(
    "/",
    summary="List of all categories",
    description="Fetch a list of all expense and budget categories.",
    status_code=status.HTTP_200_OK,
)
async def get_all_categories(
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> list[CategoryResponse]:
    return await service.get_all_categories()


@router.post(
    "/",
    summary="Create category",
    description="Create a new category alongside its assigned budget goal.",
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    data: CategoryCreate,
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryResponse:
    return await service.add_category(data.model_dump())


@router.patch(
    "/{category_id}",
    summary="Edit a category",
    description="Partially update a category name or its budget goal. Only provided fields are updated.",
    status_code=status.HTTP_200_OK,
)
async def edit_category(
    category_id: Annotated[int, Path(gt=0)],
    data: CategoryUpdate,
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryResponse:
    updated_data = data.model_dump(exclude_unset=True)
    return await service.edit_category(category_id, updated_data)


@router.delete(
    "/{category_id}",
    summary="Delete a category",
    description="Permanently delete a category and its associated budget from the database.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    category_id: Annotated[int, Path(gt=0)],
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> None:
    await service.delete_category(category_id)

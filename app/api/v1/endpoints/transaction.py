from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.dependencies import get_transaction_service
from app.schemas import TransactionCreate, TransactionResponse, TransactionUpdate
from app.service import TransactionService

router = APIRouter()


@router.get(
    "/{transaction_id}",
    summary="Get single transaction",
    status_code=status.HTTP_200_OK,
)
async def get_transaction(
    transaction_id: Annotated[int, Path(gt=0)],
    service: Annotated[TransactionService, Depends(get_transaction_service)],
) -> TransactionResponse:
    return await service.get_transaction(transaction_id)


@router.get(
    "/",
    summary="List of all transactions",
    status_code=status.HTTP_200_OK,
)
async def get_all_transaction(
    service: Annotated[TransactionService, Depends(get_transaction_service)],
) -> list[TransactionResponse]:
    return await service.get_all_transactions()


@router.post(
    "/",
    summary="Create a transaction",
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    data: TransactionCreate,
    service: Annotated[TransactionService, Depends(get_transaction_service)],
) -> TransactionResponse:
    return await service.add_transaction(data.model_dump())


@router.patch(
    "/{transaction_id}",
    summary="Edit a transaction",
    status_code=status.HTTP_200_OK,
)
async def edit_transaction(
    transaction_id: Annotated[int, Path(gt=0)],
    data: TransactionUpdate,
    service: Annotated[TransactionService, Depends(get_transaction_service)],
) -> TransactionResponse:
    update_data = data.model_dump(exclude_unset=True)
    return await service.edit_transaction(transaction_id, update_data)


@router.delete(
    "/{transaction_id}",
    summary="Delete a transaction",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_transaction(
    transaction_id: Annotated[int, Path(gt=0)],
    service: Annotated[TransactionService, Depends(get_transaction_service)],
) -> None:
    return await service.delete_transaction(transaction_id)

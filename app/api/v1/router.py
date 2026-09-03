from fastapi import APIRouter

from app.api.v1.endpoints.category import router as category_route
from app.api.v1.endpoints.compute import router as compute_route
from app.api.v1.endpoints.transaction import router as transaction_route

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(
    category_route,
    prefix="/categories",
    tags=["Categories"],
)

v1_router.include_router(
    transaction_route,
    prefix="/transactions",
    tags=["Transactions"],
)

v1_router.include_router(
    compute_route,
    prefix="/compute",
    tags=["Compute"],
)

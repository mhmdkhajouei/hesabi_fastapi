from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.validators import NormalizedEmail, StrongPassword


class CategoryBase(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "name": "Supermarket",
                "budget_goal": 8000000,
            }
        },
    )

    name: str = Field(min_length=1, max_length=20, examples=["Fast Food"])
    budget_goal: int = Field(gt=0, examples=[500000])


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(
        default=None, min_length=1, max_length=20, examples=["Sport"]
    )
    budget_goal: int | None = Field(default=None, gt=0, examples=[700000])


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Supermarket",
                "budget_goal": 8000000,
            }
        },
    )

    id: int = Field(examples=[2])


class TransactionBase(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "amount": 150000,
                "type": "income",
                "date": "2026-08-30T10:30:00Z",
                "note": "Freelance project payment",
                "category_id": 5,
            }
        },
    )

    amount: int = Field(gt=0, examples=[150000])
    type: Literal["income", "expense"] = Field(examples=["income"])
    date: datetime | None = Field(default=None, examples=["2026-08-30T10:30:00Z"])
    note: str | None = Field(max_length=225, default=None, examples=["this is a note"])
    category_id: int | None = Field(gt=0, default=None, examples=[5])


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "amount": 130000,
                "note": "Updated payment note",
            }
        },
    )

    amount: int | None = Field(gt=0, default=None, examples=[130000])
    type: Literal["income", "expense"] | None = Field(
        default=None, examples=["expense"]
    )


class TransactionResponse(TransactionBase):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 2,
                "amount": 150000,
                "type": "income",
                "currency": "TOMAN",
                "date": "2026-08-30T10:30:00Z",
                "note": "Freelance project payment",
                "category_id": 5,
            }
        },
    )

    id: int = Field(gt=0, examples=[2])
    currency: str = Field(default="TOMAN", examples=["TOMAN"])
    date: datetime = Field(examples=["2026-08-30T10:30:00Z"])


class FinancialSummaryResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "income": 400000,
                "expense": 120000,
                "total": 280000,
                "currency": "TOMAN",
            }
        }
    )

    income: int = Field(examples=[400000])
    expense: int = Field(examples=[120000])
    total: int = Field(examples=[280000])
    currency: str = Field(default="TOMAN", examples=["TOMAN"])


class CategoryBalanceResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Fast Food",
                "budget_goal": 5000000,
                "spent": 5200000,
                "remaining": -200000,
            }
        }
    )

    name: str = Field(min_length=1, max_length=20, examples=["fast food"])
    budget_goal: int = Field(gt=0, examples=[5000000])
    spent: int = Field(ge=0, examples=[100000])
    remaining: int = Field(examples=[-200000])


class UserBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    email: NormalizedEmail
    name: str | None = Field(default=None, min_length=1, max_length=150, examples=[])


class UserRegister(UserBase):
    password: StrongPassword = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    email: NormalizedEmail
    password: str


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool
    created_at: datetime


class UserCreateInternal(UserBase):
    password_hash: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str = Field(min_length=1)
    exp: int = Field()
    iat: int = Field()
    nbf: int | None = Field(default=None)
    iss: str | None = Field(default=None)
    aud: str | None = Field(default=None)
    jti: str | None = Field(default=None)

    type: Literal["access", "refresh"] = Field()


class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(
        min_length=100,
        pattern=r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$",
    )


class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

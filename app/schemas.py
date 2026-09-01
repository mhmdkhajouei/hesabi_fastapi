from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class CategoryBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=20, examples=["Fast Food"])
    budget_goal: int = Field(gt=0, examples=[500000])

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: str | None = Field(default=None ,min_length=1, max_length=20, examples=["Sport"])
    budget_goal: int | None = Field(default=None ,gt=0, examples=[700000])

class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(examples=[2])



class TransactionBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    amount: int = Field(gt=0, examples=[150000])
    type: Literal["income", "expense"] = Field(examples=["income"])
    date: datetime | None = Field(default=None, examples=["2026-08-30T10:30:00Z"])
    note: str | None = Field(max_length=225, default=None, examples=["this is a note"])
    category_id: int | None = Field(gt=0, default=None, examples=[5])

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(TransactionBase):
    amount: int | None = Field(gt=0, default=None, examples=[130000])
    type: Literal["income", "expense"] | None = Field(default=None, examples=["expense"])

class TransactionResponse(TransactionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(gt=0, examples=[2])
    currency: str = Field(default="TOMAN" ,examples=["TOMAN"])
    date: datetime = Field(examples=["2026-08-30T10:30:00Z"])



from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class TokenBase(BaseModel):
    cmc_id: int = Field(example=1)
    symbol: str = Field(exmample='BTC')
    name: str = Field(example='Bitcoin')
    slug: str = Field(example='bitcoin')

    class Config:
        orm_mode = True


class TokenCreate(TokenBase):
    cmc_id: int
    is_active: Optional[bool] = True


class TokenPrice(BaseModel):
    token: TokenBase
    price: Decimal


class TokensCount(BaseModel):
    count: int = Field(example=3)

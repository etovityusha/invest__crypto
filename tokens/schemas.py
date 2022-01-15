from typing import Optional

from pydantic import BaseModel, Field


class TokenBase(BaseModel):
    id: int = Field(example=1)
    symbol: str = Field(exmample='BTC')

    class Config:
        orm_mode = True


class TokenCreate(TokenBase):
    cmc_id: int
    is_active: Optional[bool] = True

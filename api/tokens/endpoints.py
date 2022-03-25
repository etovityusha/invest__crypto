from typing import List

import httpx
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy import func

from core.coinmarketcap import CoinMarketCap
from core.prices import get_token_prices
from core.sql_app.database import get_db
from core.sql_app.models import Token
from api.tokens.schemas import TokenBase, TokenPrice, TokensCount

router = APIRouter(
    prefix="/tokens",
    tags=["tokens"],
)


@router.get('/{cmc_id}', response_model=TokenBase)
def token_detail(cmc_id: int, session=Depends(get_db)):
    """
    Get detail info about coin
    """
    obj = session.query(Token).filter(Token.cmc_id == cmc_id).first()
    return obj


@router.post("/check_new", response_model=TokensCount)
def check_new_tokens(session=Depends(get_db)):
    """
    Get new tokens on coinmarketcap and add information about them to the database
    """
    async with httpx.AsyncClient() as client:
        new_tokens_count = CoinMarketCap.check_new_tokens(client, session)
    return TokensCount(count=new_tokens_count)


@router.get("/price/", response_model=List[TokenPrice])
async def token_price(symbol: str = None, cmc_id: int = None, session=Depends(get_db)):
    """
    Get current token(s) price by id/symbol
    """
    if symbol and cmc_id:
        raise HTTPException(400, 'Choose only one of the two parameters')
    if cmc_id:
        tokens = session.query(Token).filter_by(cmc_id=cmc_id).all()
    elif symbol:
        tokens = session.query(Token).filter(
            func.lower(Token.symbol) == symbol.lower(),
        ).all()
    else:
        raise HTTPException(400, 'Query params validation failed.')
    if not tokens:
        raise HTTPException(404, 'Tokens not found. Try execute /check_new_tokens/ first.')
    result = await get_token_prices(tokens)
    return [TokenPrice(token=token, price=price) for token, price in result.items()]

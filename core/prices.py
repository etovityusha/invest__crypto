import asyncio
from decimal import Decimal
from typing import List

import httpx

from core.coinmarketcap import CoinMarketCap
from core.sql_app.models import Token


async def get_token_prices(tokens: List[Token]) -> dict[Token, Decimal]:
    async with httpx.AsyncClient() as client:
        tasks = [CoinMarketCap.get_token_price(client, token.cmc_id) for token in tokens]
        prices = await asyncio.gather(*tasks)
    return dict(zip(tokens, prices))

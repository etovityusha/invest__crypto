from decimal import Decimal

import httpx
import requests

from core.sql_app.models import Token


class CoinMarketCap:
    @classmethod
    async def get_token_price(cls, client: httpx.AsyncClient, cmc_id: int) -> Decimal:
        """
        :param client: httpx AsyncClient
        :param cmc_id: token id in coinmarketcap.com
        :return: current token price
        """
        response = await client.get(
            url=f'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart?id={cmc_id}&range=1h'
        )
        response = response.json()
        points = response['data']['points']
        last_update_timestamp = max(points.keys())
        return Decimal(points[last_update_timestamp]['v'][0])

    @classmethod
    def check_new_tokens(cls, session) -> int:
        """
        :param session: database session
        :return: new tokens count
        """
        db_tokens = set((x[0] for x in session.query(Token.cmc_id).all()))
        request = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/map',
                               headers={'X-CMC_PRO_API_KEY': 'bbf1e915-69fc-42c1-885c-98291ea05cb4'})
        if request.status_code != 200:
            raise ConnectionError('CoinMarketCap API connection problems')
        request_json = request.json()
        cmc_tokens = set([x['id'] for x in request_json['data']])
        new_tokens = cmc_tokens - db_tokens
        for token in request_json['data']:
            if token['id'] in new_tokens:
                session.add(Token(
                    symbol=token['symbol'], cmc_id=token['id'],
                    is_active=token['is_active'],
                    name=token['name'], slug=token['slug']
                ))
        session.commit()
        return len(new_tokens)

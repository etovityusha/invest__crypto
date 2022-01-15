import datetime

import requests
from fastapi import Depends, APIRouter

from sql_app.database import get_db
from sql_app.models import Token
from tokens.schemas import TokenBase

router = APIRouter(
    prefix="/tokens",
    tags=["tokens"],
    responses={404: {"description": "Not found"}},
)


@router.get('/{token_id}', response_model=TokenBase)
def token_detail(token_id: int, session=Depends(get_db)):
    obj = session.query(Token).filter(Token.id == token_id).first()
    return obj


@router.post("/check_new")
def check_new_tokens(session=Depends(get_db)):
    db_tokens = set((x[0] for x in session.query(Token.symbol).all()))
    request = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/map',
                           headers={'X-CMC_PRO_API_KEY': 'bbf1e915-69fc-42c1-885c-98291ea05cb4'})
    assert request.status_code == 200
    request_json = request.json()
    cmc_tokens = set([x['symbol'] for x in request_json['data']])
    new_tokens = cmc_tokens - db_tokens
    new_tokens_count = 0
    for token in request_json['data']:
        if token['symbol'] not in new_tokens:
            continue
        session.add(Token(symbol=token['symbol'], cmc_id=token['id'], is_active=token['is_active']))
        new_tokens_count += 1
    session.commit()
    return {'success': True, 'new_tokens_count': new_tokens_count}


@router.post("/update_price")
def update_price(token_id, session=Depends(get_db)):
    token = session.query(Token).filter_by(id=token_id).first()
    response = requests.get(f'https://api.coinmarketcap.com/data-api/v3/'
                            f'cryptocurrency/detail/chart?id={token.cmc_id}&range=1h')
    points = response.json()['data']['points']
    last_update_timestamp = max(points.keys())
    last_price = points[last_update_timestamp]['v'][0]
    token.price = last_price
    token.price_last_update = datetime.datetime.fromtimestamp(int(last_update_timestamp))
    session.commit()
    return {'success': True}


@router.get("/{symbol}/price")
def token_price(symbol: str, session=Depends(get_db)):
    token = session.query(Token).filter_by(symbol=symbol).first()
    if not token:
        raise ValueError('Token not found. Try execute /check_new_tokens/ first.')
    response = requests.get(f'https://api.coinmarketcap.com/data-api/v3/'
                            f'cryptocurrency/detail/chart?id={token.cmc_id}&range=1h')
    points = response.json()['data']['points']
    last_update_timestamp = max(points.keys())
    price = points[last_update_timestamp]['v'][0]
    return {'success': True, "symbol": symbol, "price": price}

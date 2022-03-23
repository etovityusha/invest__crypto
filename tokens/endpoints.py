from typing import List

import requests
from fastapi import Depends, APIRouter, HTTPException

from sql_app.database import get_db
from sql_app.models import Token
from tokens.schemas import TokenBase, TokenPrice

router = APIRouter(
    prefix="/tokens",
    tags=["tokens"],
    responses={404: {"description": "Not found"}},
)


@router.get('/{cmc_id}', response_model=TokenBase)
def token_detail(cmc_id: int, session=Depends(get_db)):
    obj = session.query(Token).filter(Token.cmc_id == cmc_id).first()
    return obj


@router.post("/check_new")
def check_new_tokens(session=Depends(get_db)):
    db_tokens = set((x[0] for x in session.query(Token.cmc_id).all()))
    request = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/map',
                           headers={'X-CMC_PRO_API_KEY': 'bbf1e915-69fc-42c1-885c-98291ea05cb4'})
    assert request.status_code == 200
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
    return {'success': True, 'new_tokens_count': len(new_tokens)}


@router.get("/price/", response_model=List[TokenPrice])
def token_price(symbol: str = None, cmc_id: int = None, session=Depends(get_db)):
    if symbol and cmc_id:
        raise HTTPException(400, 'Choose only one of the two parameters')
    if cmc_id:
        tokens = session.query(Token).filter_by(cmc_id=cmc_id).all()
    elif symbol:
        tokens = session.query(Token).filter_by(symbol=symbol).all()
    else:
        raise HTTPException(400, 'Query params validation failed.')
    if not tokens:
        raise HTTPException(404, 'Tokens not found. Try execute /check_new_tokens/ first.')
    result = []
    for token in tokens:
        response = requests.get(f'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/'
                                f'chart?id={token.cmc_id}&range=1h')
        points = response.json()['data']['points']
        last_update_timestamp = max(points.keys())
        price = points[last_update_timestamp]['v'][0]
        result.append(TokenPrice(token=TokenBase.from_orm(token), price=price))
    return result

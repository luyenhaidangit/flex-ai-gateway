from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.securities_repository import SecuritiesRepository
from app.schemas import (
    ErrorDetail,
    SecuritiesAdviceResponse,
    SecuritiesInfoResponse,
    SecuritiesPriceChangeRequest,
)
from app.services.securities_service import SecuritiesService

router = APIRouter(prefix="/stock", tags=["Securities"])


@router.post(
    "/price-change",
    response_model=SecuritiesInfoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create stock price change information",
)
async def create_stock_price_change(
    request: SecuritiesPriceChangeRequest,
    db: AsyncSession = Depends(get_db),
):
    service = SecuritiesService(SecuritiesRepository(db))
    return await service.create_price_change(request)


@router.get(
    "/advice/{symbol}",
    response_model=SecuritiesAdviceResponse,
    summary="Get investment advice for a stock symbol",
    responses={404: {"model": ErrorDetail, "description": "Stock symbol not found"}},
)
async def get_stock_advice(symbol: str, db: AsyncSession = Depends(get_db)):
    service = SecuritiesService(SecuritiesRepository(db))
    advice = await service.get_advice(symbol)

    if advice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock symbol {symbol.upper()} not found",
        )

    return advice

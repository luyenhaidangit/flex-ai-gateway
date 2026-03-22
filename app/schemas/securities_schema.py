from datetime import datetime

from pydantic import BaseModel, Field


class SecuritiesAdviceResponse(BaseModel):
    """Response body for GET /stock/advice/{symbol}."""

    symbol: str = Field(description="Stock symbol")
    recommendation: str = Field(description="Investment recommendation such as BUY, HOLD, or SELL")
    confidence: float = Field(description="Recommendation confidence score from 0.0 to 1.0")


class SecuritiesPriceChangeRequest(BaseModel):
    """Request body for POST /stock/price-change."""

    symbol: str = Field(min_length=1, max_length=20, description="Stock symbol")
    trade_time: datetime = Field(description="Trade timestamp")
    price: float = Field(gt=0, description="Latest traded price")
    volume: int = Field(ge=0, description="Traded volume")
    change_percent: float = Field(ge=-100, le=100, description="Percentage price change")


class SecuritiesInfoResponse(BaseModel):
    """Response body for persisted securities market data."""

    id: int
    symbol: str
    trade_time: datetime
    price: float
    volume: int
    change_percent: float

    class Config:
        from_attributes = True

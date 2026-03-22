from decimal import Decimal

from app.models.securities_info import SecuritiesInfo
from app.repositories.securities_repository import SecuritiesRepository
from app.schemas.securities_schema import SecuritiesAdviceResponse
from app.schemas.securities_schema import SecuritiesInfoResponse
from app.schemas.securities_schema import SecuritiesPriceChangeRequest


class SecuritiesService:
    """Business logic for securities investment advice."""

    def __init__(self, repo: SecuritiesRepository):
        self.repo = repo

    async def create_price_change(
        self, request: SecuritiesPriceChangeRequest
    ) -> SecuritiesInfoResponse:
        entry = await self.repo.create(
            symbol=request.symbol,
            trade_time=request.trade_time,
            price=request.price,
            volume=request.volume,
            change_percent=request.change_percent,
        )
        return self._to_info_response(entry)

    async def get_advice(self, symbol: str) -> SecuritiesAdviceResponse | None:
        record = await self.repo.get_latest_by_symbol(symbol)
        if record is None:
            return None

        change_percent = float(record.change_percent or Decimal("0"))
        recommendation = self._get_recommendation(change_percent)
        confidence = self._get_confidence(change_percent, recommendation)

        return SecuritiesAdviceResponse(
            symbol=record.symbol,
            recommendation=recommendation,
            confidence=confidence,
        )

    def _to_info_response(self, entry: SecuritiesInfo) -> SecuritiesInfoResponse:
        return SecuritiesInfoResponse(
            id=entry.id,
            symbol=entry.symbol,
            trade_time=entry.trade_time,
            price=float(entry.price),
            volume=entry.volume,
            change_percent=float(entry.change_percent),
        )

    def _get_recommendation(self, change_percent: float) -> str:
        if change_percent > 0:
            return "BUY"
        if change_percent < 0:
            return "SELL"
        return "HOLD"

    def _get_confidence(self, change_percent: float, recommendation: str) -> float:
        if recommendation == "HOLD":
            return 0.6

        normalized = min(abs(change_percent), 1.0)
        return round(min(0.7 + normalized * 0.4, 0.95), 2)

import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.securities_info import SecuritiesInfo

logger = logging.getLogger(__name__)


class SecuritiesRepository:
    """Data access layer for SECURITIES_INFO records."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        symbol: str,
        trade_time: datetime,
        price: float,
        volume: int,
        change_percent: float,
    ) -> SecuritiesInfo:
        entry = SecuritiesInfo(
            symbol=symbol.upper(),
            trade_time=trade_time,
            price=Decimal(str(price)),
            volume=volume,
            change_percent=Decimal(str(change_percent)),
        )
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def get_by_id(self, security_id: int) -> SecuritiesInfo | None:
        """Retrieve a market data record by its primary key."""
        try:
            stmt = select(SecuritiesInfo).where(SecuritiesInfo.id == security_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as exc:
            logger.error(f"Error reading securities info by id from DB: {exc}")
            return None

    async def get_latest_by_symbol(self, symbol: str) -> SecuritiesInfo | None:
        """Retrieve the latest market data record for a symbol."""
        try:
            stmt = (
                select(SecuritiesInfo)
                .where(SecuritiesInfo.symbol == symbol.upper())
                .order_by(SecuritiesInfo.trade_time.desc(), SecuritiesInfo.id.desc())
            )
            result = await self.db.execute(stmt)
            return result.scalars().first()
        except Exception as exc:
            logger.error(f"Error reading latest securities info by symbol from DB: {exc}")
            return None

    async def list_by_symbol(self, symbol: str, limit: int = 50) -> list[SecuritiesInfo]:
        """List market data records for a symbol ordered by newest trade time first."""
        try:
            stmt = (
                select(SecuritiesInfo)
                .where(SecuritiesInfo.symbol == symbol.upper())
                .order_by(SecuritiesInfo.trade_time.desc(), SecuritiesInfo.id.desc())
                .limit(limit)
            )
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as exc:
            logger.error(f"Error listing securities info by symbol from DB: {exc}")
            return []

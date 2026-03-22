from sqlalchemy import BigInteger, Column, DateTime, Identity, Numeric, String

from app.database import Base


class SecuritiesInfo(Base):
    """ORM model for market data records stored in SECURITIES_INFO."""

    __tablename__ = "SECURITIES_INFO"

    id = Column("ID", BigInteger, Identity(start=1), primary_key=True, autoincrement=True)
    symbol = Column("SYMBOL", String(20), nullable=False)
    trade_time = Column("TRADE_TIME", DateTime, nullable=False)
    price = Column("PRICE", Numeric(18, 4), nullable=False)
    volume = Column("VOLUME", BigInteger, nullable=False)
    change_percent = Column("CHANGE_PERCENT", Numeric(8, 4), nullable=False)

    def __repr__(self) -> str:
        return (
            "<SecuritiesInfo("
            f"id={self.id}, "
            f"symbol='{self.symbol}', "
            f"trade_time={self.trade_time}, "
            f"price={self.price}, "
            f"volume={self.volume}, "
            f"change_percent={self.change_percent}"
            ")>"
        )

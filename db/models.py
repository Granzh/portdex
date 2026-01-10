from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)

from .base import Base


class Security(Base):
    """Security data model"""

    __tablename__ = "securities"

    ticker = Column(String, primary_key=True)
    board = Column(String)
    engine = Column(String)
    currency = Column(String)


class Candle(Base):
    """Candle data model"""

    __tablename__ = "candles"

    ticker = Column(ForeignKey("securities.ticker"), primary_key=True)
    datetime = Column(DateTime, primary_key=True)
    # интервал сканирования, в минутах
    interval = Column(Integer, primary_key=True)

    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)

    __table_args__ = (Index("ix_candles_ticker_datetime", "ticker", "datetime"),)


class PortfolioSnapshot(Base):
    """Portfolio snapshot data model"""

    __tablename__ = "portfolio_snapshots"

    datetime = Column(DateTime, primary_key=True)
    total_value = Column(Float)


class PortfolioIndex(Base):
    """Portfolio index data model"""

    __tablename__ = "portfolio_index"

    datetime = Column(DateTime, primary_key=True)
    index_value = Column(Float)

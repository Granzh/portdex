from datetime import datetime as dt

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
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm.base import Mapped

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

    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume = Column(BigInteger)

    __table_args__ = (Index("ix_candles_ticker_datetime", "ticker", "datetime"),)


class PortfolioSnapshotPosition(Base):
    __tablename__ = "portfolio_snapshot_positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    snapshot_datetime: Mapped[dt] = mapped_column(
        DateTime, ForeignKey("portfolio_snapshots.datetime"), index=True
    )
    ticker: Mapped[str] = mapped_column(String, index=True)
    quantity: Mapped[float] = mapped_column(Float)


class PortfolioSnapshot(Base):
    """Portfolio snapshot data model"""

    __tablename__ = "portfolio_snapshots"

    datetime: Mapped[dt] = mapped_column(DateTime, primary_key=True)
    total_value: Mapped[float] = mapped_column(Float)

    positions: Mapped[list["PortfolioSnapshotPosition"]] = relationship(
        backref="snapshot", cascade="all, delete-orphan", lazy="joined"
    )


class PortfolioIndex(Base):
    """Portfolio index data model"""

    __tablename__ = "portfolio_index"

    datetime: Mapped[dt] = mapped_column(DateTime, primary_key=True)
    index_value: Mapped[float] = mapped_column(Float)

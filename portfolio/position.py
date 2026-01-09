from dataclasses import dataclass


@dataclass
class Position:
    """Позиция по одному тикеру"""

    ticker: str
    quantity: int
    cash_flow: float  # сколько денег вложено с учетом комисии (BUY - отрицательное, SELL - положительное)

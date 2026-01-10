from dataclasses import dataclass


@dataclass
class Position:
    """Represents a position in a portfolio for a single ticker"""

    ticker: str
    quantity: int
    cash_flow: float  # сколько денег вложено с учетом комисии (BUY - отрицательное, SELL - положительное)

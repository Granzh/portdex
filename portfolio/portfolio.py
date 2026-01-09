from portfolio.position import Position


class Portfolio:
    """Состояние портфеля"""

    def __init__(self):
        self.positions: dict[str, Position] = {}
        self.cash: float = 0.0

    def apply_trade(self, trade):
        pos = self.positions.get(trade.ticker)

        if not pos:
            pos = Position(trade.ticker, 0, 0.0)
            self.positions[trade.ticker] = pos

        if trade.operation == "BUY":
            pos.quantity += trade.quantity
            pos.cash_flow -= trade.price * trade.quantity + trade.fee

        if trade.operation == "SELL":
            pos.quantity -= trade.quantity
            pos.cash_flow += trade.price * trade.quantity - trade.fee

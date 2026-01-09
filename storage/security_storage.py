from sqlalchemy.orm import Session

from db.models import Security


class SecurityStorage:
    def __init__(self, session: Session):
        self.session = session

    def get_or_create(
        self,
        *,
        ticker: str,
        board: str = "TQBR",
        engine: str = "stock",
        currency: str = "RUB",
    ) -> Security:
        sec = self.session.get(Security, ticker)

        if sec:
            return sec

        sec = Security(ticker=ticker, board=board, engine=engine, currency=currency)

        self.session.add(sec)
        self.session.commit()
        return sec

from sqlalchemy.orm import Session

from db.models import PortfolioIndex


class IndexStorage:
    def __init__(self, session: Session):
        self.session = session

    def save_point(self, datetime, value: float):
        self.session.merge(PortfolioIndex(datetime=datetime, value=value))
        self.session.commit()

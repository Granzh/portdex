from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.models import PortfolioIndex


class PortfolioIndexStorage:
    def __init__(self, session: Session):
        self.session = session

    def save(self, index: PortfolioIndex) -> bool:
        self.session.add(index)
        try:
            self.session.commit()
            return True
        except IntegrityError:
            self.session.rollback()
            return False

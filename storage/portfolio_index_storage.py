from sqlalchemy.orm import Session

from db.models import PortfolioIndex


class PortfolioIndexStorage:
    """
    Provides methods for saving and retrieving portfolio index data.
    """

    def __init__(self, session: Session):
        self.session = session

    def save(self, index: PortfolioIndex) -> bool:
        """
        Saves a portfolio index.
        """
        self.session.add(index)
        try:
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False

    def get_all_ordered(self) -> list[PortfolioIndex]:
        return (
            self.session.query(PortfolioIndex)
            .order_by(PortfolioIndex.datetime.asc())
            .all()
        )

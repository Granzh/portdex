from sqlalchemy.orm import Session

from db.models import PortfolioIndex


class IndexStorage:
    """
    Provides methods for saving and retrieving portfolio index data.
    """

    def __init__(self, session: Session):
        self.session = session

    def save_point(self, datetime, value: float) -> None:
        """
        Saves a portfolio index point.
        """
        self.session.merge(PortfolioIndex(datetime=datetime, value=value))
        self.session.commit()

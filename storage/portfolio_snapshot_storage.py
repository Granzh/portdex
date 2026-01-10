from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import PortfolioSnapshot


class PortfolioSnapshotStorage:
    """
    Provides methods for saving and retrieving portfolio snapshot data.
    """

    def __init__(self, session: Session):
        self.session = session

    def save(self, snapshot: PortfolioSnapshot) -> bool:
        """
        Saves a portfolio snapshot.
        """
        self.session.add(snapshot)
        try:
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False

    def get_first(self) -> PortfolioSnapshot | None:
        """
        Retrieves the first portfolio snapshot.
        """

        stmt = (
            select(PortfolioSnapshot)
            .where(PortfolioSnapshot.total_value > 0)
            .order_by(PortfolioSnapshot.datetime)
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_last(self) -> PortfolioSnapshot | None:
        """
        Retrieves the last portfolio snapshot.
        """
        return (
            self.session.query(PortfolioSnapshot)
            .order_by(PortfolioSnapshot.datetime.desc())
            .first()
        )

    def get_all_ordered(self) -> list[PortfolioSnapshot]:
        """
        Retrieves all portfolio snapshots ordered by datetime.
        """
        return (
            self.session.query(PortfolioSnapshot)
            .order_by(PortfolioSnapshot.datetime.asc())
            .all()
        )

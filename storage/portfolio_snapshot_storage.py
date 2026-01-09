from sqlalchemy.orm import Session

from db.models import PortfolioSnapshot


class PortfolioSnapshotStorage:
    def __init__(self, session: Session):
        self.session = session

    def save(self, snapshot: PortfolioSnapshot) -> bool:
        self.session.add(snapshot)
        try:
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False

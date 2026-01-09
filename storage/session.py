from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base import Base

engine = create_engine("sqlite:///./db/sqlite3", echo=False, future=True)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def init_db():
    Base.metadata.create_all(bind=engine)

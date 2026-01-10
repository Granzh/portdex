from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base import Base

engine = None
SessionLocal = None


def init_db():
    global engine, SessionLocal
    engine = create_engine("sqlite:///./db/sqlite3", echo=False, future=True)
    SessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )
    Base.metadata.create_all(bind=engine)

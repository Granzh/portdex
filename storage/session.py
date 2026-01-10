from typing import Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from db.base import Base

engine: Optional[Engine] = None
SessionLocal: Optional[sessionmaker[Session]] = None


def init_db():
    global engine, SessionLocal
    try:
        print("Initializing database...")
        engine = create_engine("sqlite:///./db/sqlite3", echo=False, future=True)
        print(f"Engine created: {engine}")

        SessionLocal = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
        )
        print(f"SessionLocal created: {SessionLocal}")

        Base.metadata.create_all(bind=engine)
        print("Database tables created")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
from sqlalchemy.orm import Session


def get_db():

    db: Session = SessionLocal()

    try:
        yield db

    finally:
        db.close()
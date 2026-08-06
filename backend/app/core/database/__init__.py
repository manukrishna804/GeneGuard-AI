from app.core.database.base import Base
from app.core.database.session import engine


def init_db():
    Base.metadata.create_all(bind=engine)
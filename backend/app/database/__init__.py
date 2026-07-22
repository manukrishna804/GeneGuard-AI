from app.database.base import Base
from app.database.session import engine


def init_db():
    Base.metadata.create_all(bind=engine)
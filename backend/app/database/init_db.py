from app.database.base import Base
from app.database.session import engine

# Import all models here
from app.models import Patient


def init_db():
    Base.metadata.create_all(bind=engine)
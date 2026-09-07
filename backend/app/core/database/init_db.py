from app.core.database.base import Base
from app.core.database.session import engine

# Import all models here
from app.modules.patient.model import Patient
from app.modules.wes_analysis.model import WESReport
from app.modules.pharmacogenomics.model import PGxReport


def init_db():
    Base.metadata.create_all(bind=engine)
from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS alembic_version'))
    conn.execute(text('CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY)'))
    conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('6512906493ab')"))
    conn.commit()

print("Successfully reset alembic_version")

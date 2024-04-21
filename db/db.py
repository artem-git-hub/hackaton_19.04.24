from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from db.models import Base

from config import config


DATABASE_URL = f"postgresql://{config.db.user}:{config.db.password}@{config.db.container}:5432/{config.db.database}"

engine = create_engine(DATABASE_URL)
# Base.metadata.drop_all(bind=engine, checkfirst=True)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

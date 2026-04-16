from sqlmodel import create_engine, Session
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# Engine is globally configured here
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

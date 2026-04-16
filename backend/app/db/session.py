from contextlib import contextmanager
from sqlmodel import create_engine, Session
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# Engine is globally configured here
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    """FastAPI依存性注入用のセッション生成"""
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_context():
    """
    Celeryタスクなどで使用するセッションコンテキストマネージャ
    自動でコミット・ロールバックを行う
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

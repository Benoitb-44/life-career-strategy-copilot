from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

DEFAULT_DB_URL = "sqlite:///./copilot.db"

DATABASE_URL = settings.database_url or DEFAULT_DB_URL
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)


def create_db_and_tables() -> None:
    import app.models  # noqa: F401 - ensure SQLModel metadata is populated

    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session

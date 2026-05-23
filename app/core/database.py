"""
Database engine and session management.
"""
from sqlmodel import SQLModel, create_engine, Session, text
from app.core.config import settings

# Create database engine
engine = create_engine(settings.DATABASE_URL, echo=False)


def init_db():
    """
    Initialize the database.
    Creates pgvector extension and all tables.
    """
    # Ensure pgvector extension exists before creating tables
    with Session(engine) as session:
        session.exec(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        session.commit()

    # Create all tables
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Dependency for getting database sessions.
    Yields a session that automatically closes after use.
    """
    with Session(engine) as session:
        yield session

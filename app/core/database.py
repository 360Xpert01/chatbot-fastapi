"""
Database engine and session management.
"""
from sqlmodel import SQLModel, create_engine, Session, text
from app.core.config import settings

# Create database engine
engine = create_engine(settings.DATABASE_URL, echo=False)


def ensure_vector_dimension():
    """
    Adjust document_embeddings.embedding vector dimension to match
    settings.EMBEDDING_DIMENSION if it differs from the current column type.
    This handles cases where the DB schema was created with a different dimension.
    """
    try:
        with Session(engine) as session:
            result = session.exec(text(
                "SELECT atttypmod FROM pg_attribute "
                "WHERE attrelid = 'document_embeddings'::regclass "
                "AND attname = 'embedding';"
            )).first()
            if result is not None:
                typmod = result[0]
                # pgvector stores dimension directly in atttypmod
                current_dim = typmod - 4 if typmod > 0 else typmod
                expected = settings.EMBEDDING_DIMENSION
                if current_dim != expected:
                    session.exec(text(
                        f"ALTER TABLE document_embeddings "
                        f"ALTER COLUMN embedding TYPE vector({expected});"
                    ))
                    session.commit()
                    print(f"Adjusted embedding dimension from {current_dim} to {expected}")
    except Exception as e:
        # Table may not exist yet on first run — that's fine
        print(f"Note: Could not adjust embedding dimension (may not exist yet): {e}")


def init_db():
    """
    Initialize the database.
    Creates pgvector extension and all tables.
    Also ensures the embedding vector dimension matches settings.EMBEDDING_DIMENSION.
    """
    # Ensure pgvector extension exists before creating tables
    with Session(engine) as session:
        session.exec(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        session.commit()

    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Align the embedding column dimension with current config
    ensure_vector_dimension()


def get_session():
    """
    Dependency for getting database sessions.
    Yields a session that automatically closes after use.
    """
    with Session(engine) as session:
        yield session

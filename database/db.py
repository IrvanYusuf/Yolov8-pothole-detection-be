# database.py
from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# The `echo=True` will log all SQL queries, which is useful for debugging.
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """Create database tables based on SQLModel metadata."""
    print("Creating tables...")
    SQLModel.metadata.create_all(engine)
    print("Tables created.")


def get_session():
    """
    Dependency to provide a database session.
    It automatically handles session closure using a context manager.
    """
    print("Attempting to connect to the database...")
    try:
        with Session(engine) as session:
            yield session
        print("Session closed successfully.")
    except Exception as e:
        print(f"Failed to connect to the database or an error occurred: {e}")
        # Re-raise the exception to be handled by FastAPI
        raise

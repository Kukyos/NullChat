from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models.database import Base
import os

# Database URL - SQLite for development with absolute path
db_path = os.path.join(os.path.dirname(__file__), "..", "data", "database.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")

# Create engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize database tables
def init_db():
    """Initialize database tables. Called when needed."""
    Base.metadata.create_all(bind=engine)

# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
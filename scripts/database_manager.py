# database_manager.py
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os

Base = declarative_base()


class Post(Base):
    """Database model for Bluesky posts"""

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    post_id = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, index=True)
    content = Column(JSON)


class Reply(Base):
    """Database model for post replies"""

    __tablename__ = "replies"

    id = Column(Integer, primary_key=True)
    post_id = Column(String, ForeignKey("posts.post_id"), index=True)
    reply_id = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, index=True)
    content = Column(JSON)


class DatabaseManager:
    """Manager for database operations"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.engine = None
        self.SessionLocal = None
        # Expose models as class attributes
        self.Post = Post
        self.Reply = Reply

    def initialize(self):
        """Initialize database connection and create tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    @contextmanager
    def get_session(self) -> Session:
        """Provide a transactional scope around a series of operations"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

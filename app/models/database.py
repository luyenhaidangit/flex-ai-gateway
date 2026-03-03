from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base


class ChatCache(Base):
    """ORM model — stores cached AI chat responses."""

    __tablename__ = "chat_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    model = Column(String(50), nullable=False)
    prompt_hash = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_prompt_hash_model", "prompt_hash", "model"),
    )

    def __repr__(self):
        return f"<ChatCache(id={self.id}, model='{self.model}', cached_at='{self.created_at}')>"

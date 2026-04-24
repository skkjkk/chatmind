"""Chat record model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class ChatRecord(Base):
    """Chat record model"""
    __tablename__ = "chat_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    contact_name = Column(String(100), nullable=False)
    file_name = Column(String(255), nullable=True)
    file_content = Column(Text, nullable=True)  # Store original file content
    message_count = Column(Integer, default=0)
    parse_status = Column(String(20), default="pending")  # pending, success, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = relationship("Message", back_populates="record", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="record", cascade="all, delete-orphan")
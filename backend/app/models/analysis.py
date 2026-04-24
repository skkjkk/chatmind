"""Analysis result model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Analysis(Base):
    """Analysis result model"""
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    record_id = Column(String(36), ForeignKey("chat_records.id"), nullable=False, index=True)
    analysis_type = Column(String(50), nullable=False)  # stats, personality, relation
    result_data = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    record = relationship("ChatRecord", back_populates="analyses")
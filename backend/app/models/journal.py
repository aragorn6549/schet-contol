from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class JournalEntry(Base):
    __tablename__ = "journal"

    id = Column(Integer, primary_key=True, index=True)
    
    action = Column(String(100), nullable=False)
    description = Column(Text)
    entity_type = Column(String(50))  # request, counterparty, profile
    entity_id = Column(Integer)
    
    performed_by_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    performed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    performer = relationship("Profile")

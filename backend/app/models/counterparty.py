from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base
from app.core.enums import CounterpartyStatus


class Counterparty(Base):
    __tablename__ = "counterparties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    inn = Column(String(12), unique=True, nullable=False, index=True)
    kpp = Column(String(9))
    legal_address = Column(Text)
    bank_name = Column(String(255))
    bik = Column(String(9))
    checking_account = Column(String(20))
    correspondent_account = Column(String(20))
    
    status = Column(SQLEnum(CounterpartyStatus), default=CounterpartyStatus.PENDING, nullable=False)
    checked_by_id = Column(Integer, ForeignKey("profiles.id"))
    checked_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    requests = relationship("Request", back_populates="counterparty")

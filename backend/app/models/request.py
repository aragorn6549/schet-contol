from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base
from app.core.enums import RequestStatus


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    
    # Internal number: ProjectName_DealNumber_SequentialNumber
    internal_number = Column(String(100), unique=True, nullable=False, index=True)
    
    project_name = Column(String(255), nullable=False)
    deal_number = Column(String(50), nullable=False)
    invoice_number = Column(String(100), nullable=False)
    invoice_url = Column(Text, nullable=False)
    amount = Column(Numeric(15, 2))
    
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.DRAFT, nullable=False)
    
    created_by_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    counterparty_id = Column(Integer, ForeignKey("counterparties.id"), nullable=False)
    
    approved_by_id = Column(Integer, ForeignKey("profiles.id"))
    approved_at = Column(DateTime)
    
    paid_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = relationship("Profile", foreign_keys=[created_by_id], backref="created_requests")
    counterparty = relationship("Counterparty", back_populates="requests")
    approver = relationship("Profile", foreign_keys=[approved_by_id])

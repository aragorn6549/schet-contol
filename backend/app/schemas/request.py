from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.core.enums import RequestStatus


class RequestBase(BaseModel):
    project_name: str
    deal_number: str
    invoice_number: str
    invoice_url: str = Field(..., description="URL к файлу счёта")
    amount: Optional[Decimal] = None
    counterparty_id: int


class RequestCreate(RequestBase):
    pass


class RequestUpdate(BaseModel):
    status: Optional[RequestStatus] = None


class RequestResponse(RequestBase):
    id: int
    internal_number: str
    status: RequestStatus
    created_by_id: int
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RequestPPRequest(BaseModel):
    """Запрос текста письма для бухгалтерии"""
    pass

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.core.enums import CounterpartyStatus


class CounterpartyBase(BaseModel):
    name: str
    inn: str = Field(..., min_length=10, max_length=12)
    kpp: Optional[str] = None
    legal_address: Optional[str] = None
    bank_name: Optional[str] = None
    bik: Optional[str] = None
    checking_account: Optional[str] = None
    correspondent_account: Optional[str] = None


class CounterpartyCreate(CounterpartyBase):
    pass


class CounterpartyUpdate(BaseModel):
    status: CounterpartyStatus


class CounterpartyResponse(CounterpartyBase):
    id: int
    status: CounterpartyStatus
    checked_by_id: Optional[int] = None
    checked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

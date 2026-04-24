from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class JournalEntryBase(BaseModel):
    action: str
    description: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryResponse(JournalEntryBase):
    id: int
    performed_by_id: int
    performer_full_name: Optional[str] = None
    performed_at: datetime
    
    class Config:
        from_attributes = True

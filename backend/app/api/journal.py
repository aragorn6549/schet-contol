from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.journal import JournalEntry
from app.models.profile import Profile
from app.schemas.journal import JournalEntryResponse
from app.core.dependencies import get_current_profile

router = APIRouter(prefix="/api/journal", tags=["Журнал"])


@router.get("/", response_model=List[JournalEntryResponse])
def get_journal(
    skip: int = 0,
    limit: int = 100,
    entity_type: str = None,
    db: Session = Depends(get_db),
    current_profile: Profile = Depends(get_current_profile)
):
    """Получение журнала действий (все авторизованные)"""
    query = db.query(JournalEntry).order_by(JournalEntry.performed_at.desc())
    
    if entity_type:
        query = query.filter(JournalEntry.entity_type == entity_type)
    
    entries = query.offset(skip).limit(limit).all()
    
    # Добавляем имя исполнителя
    result = []
    for entry in entries:
        performer_name = None
        if entry.performer:
            performer_name = entry.performer.full_name
        
        result.append({
            "id": entry.id,
            "action": entry.action,
            "description": entry.description,
            "entity_type": entry.entity_type,
            "entity_id": entry.entity_id,
            "performed_by_id": entry.performed_by_id,
            "performer_full_name": performer_name,
            "performed_at": entry.performed_at
        })
    
    return result

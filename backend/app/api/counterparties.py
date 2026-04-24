from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.counterparty import Counterparty
from app.models.user import Profile
from app.models.journal import JournalEntry
from app.schemas.counterparty import CounterpartyCreate, CounterpartyResponse, CounterpartyUpdate
from app.core.dependencies import get_current_profile, require_role
from app.core.enums import UserRole, CounterpartyStatus

router = APIRouter(prefix="/api/counterparties", tags=["Контрагенты"])


@router.get("/", response_model=List[CounterpartyResponse])
def get_counterparties(
    skip: int = 0,
    limit: int = 100,
    status_filter: CounterpartyStatus = None,
    db: Session = Depends(get_db),
    current_profile: Profile = Depends(get_current_profile)
):
    """Получение списка контрагентов (все авторизованные)"""
    query = db.query(Counterparty)
    
    if status_filter:
        query = query.filter(Counterparty.status == status_filter)
    
    counterparties = query.offset(skip).limit(limit).all()
    return counterparties


@router.post("/", response_model=CounterpartyResponse)
def create_counterparty(
    counterparty_data: CounterpartyCreate,
    db: Session = Depends(get_db),
    current_profile: Profile = Depends(get_current_profile)
):
    """Создание нового контрагента"""
    # Проверка существующего ИНН
    existing = db.query(Counterparty).filter(Counterparty.inn == counterparty_data.inn).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Контрагент с таким ИНН уже существует"
        )
    
    counterparty = Counterparty(
        **counterparty_data.model_dump(),
        status=CounterpartyStatus.PENDING
    )
    db.add(counterparty)
    db.commit()
    db.refresh(counterparty)
    
    # Запись в журнал
    journal_entry = JournalEntry(
        action="COUNTERPARTY_CREATED",
        description=f"Создан контрагент {counterparty.name} (ИНН: {counterparty.inn})",
        entity_type="counterparty",
        entity_id=counterparty.id,
        performed_by_id=current_profile.id
    )
    db.add(journal_entry)
    db.commit()
    
    return counterparty


@router.get("/{counterparty_id}", response_model=CounterpartyResponse)
def get_counterparty(
    counterparty_id: int,
    db: Session = Depends(get_db),
    current_profile: Profile = Depends(get_current_profile)
):
    """Получение контрагента по ID"""
    counterparty = db.query(Counterparty).filter(Counterparty.id == counterparty_id).first()
    if not counterparty:
        raise HTTPException(status_code=404, detail="Контрагент не найден")
    return counterparty


@router.put("/{counterparty_id}/status", response_model=CounterpartyResponse)
def update_counterparty_status(
    counterparty_id: int,
    status_data: CounterpartyUpdate,
    db: Session = Depends(get_db),
    current_profile: Profile = Depends(require_role(UserRole.SECURITY, UserRole.ADMIN))
):
    """Обновление статуса проверки контрагента (только security и admin)"""
    counterparty = db.query(Counterparty).filter(Counterparty.id == counterparty_id).first()
    if not counterparty:
        raise HTTPException(status_code=404, detail="Контрагент не найден")
    
    counterparty.status = status_data.status
    counterparty.checked_by_id = current_profile.id
    counterparty.checked_at = datetime.utcnow()
    
    db.add(counterparty)
    db.commit()
    db.refresh(counterparty)
    
    # Запись в журнал
    journal_entry = JournalEntry(
        action="COUNTERPARTY_STATUS_UPDATED",
        description=f"Статус контрагента {counterparty.name} изменён на {status_data.status.value}",
        entity_type="counterparty",
        entity_id=counterparty.id,
        performed_by_id=current_profile.id
    )
    db.add(journal_entry)
    db.commit()
    
    return counterparty

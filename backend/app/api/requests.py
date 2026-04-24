from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.request import Request
from app.models.counterparty import Counterparty
from app.models.user import Profile
from app.models.journal import JournalEntry
from app.schemas.request import RequestCreate, RequestResponse, RequestUpdate
from app.core.dependencies import get_current_profile, require_role
from app.core.enums import UserRole, RequestStatus, CounterpartyStatus

router = APIRouter(prefix="/api/requests", tags=["Заявки"])


def generate_internal_number(db: Session, project_name: str, deal_number: str) -> str:
    """Генерация внутреннего номера заявки"""
    # Получаем количество заявок с таким же префиксом
    prefix = f"{project_name}_{deal_number}"
    count = db.query(Request).filter(
        Request.internal_number.like(f"{prefix}_%")
    ).count()
    
    sequential_number = count + 1
    return f"{prefix}_{sequential_number:03d}"


@router.get("/", response_model=List[RequestResponse])
def get_requests(
    skip: int = 0,
    limit: int = 100,
    status_filter: RequestStatus = None,
    db: Session = Depends(get_db),
    current_profile: Profile = Depends(get_current_profile)
):
    """Получение списка заявок с фильтрацией по роли"""
    query = db.query(Request)
    
    # Фильтрация по роли
    if current_profile.role == UserRole.ENGINEER:
        # Инженер видит только свои заявки
        query = query.filter(Request.created_by_id == current_profile.id)
    elif current_profile.role == UserRole.ACCOUNTANT:
        # Бухгалтер видит только согласованные и оплаченные
        query = query.filter(
            Request.status.in_([RequestStatus.APPROVED, RequestStatus.PAID])
        )
    # Директор и админ видят все заявки
    
    if status_filter:
        query = query.filter(Request.status == status_filter)
    
    requests = query.order_by(Request.created_at.desc()).offset(skip).limit(limit).all()
    return requests


@router.post("/", response_model=RequestResponse)
def create_request(
    request_data: RequestCreate,
    db: Session = Depends(get_db),
    current_profile: Profile = Depends(get_current_profile)
):
    """Создание новой заявки (только engineer)"""
    if current_profile.role != UserRole.ENGINEER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только инженеры могут создавать заявки"
        )
    
    # Проверка контрагента
    counterparty = db.query(Counterparty).filter(Counterparty.id == request_data.counterparty_id).first()
    if not counterparty:
        raise HTTPException(status_code=404, detail="Контрагент не найден")
    
    # Если контрагент отклонён - ошибка
    if counterparty.status == CounterpartyStatus.REJECTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Контрагент отклонён отделом безопасности"
        )
    
    # Генерация внутреннего номера
    internal_number = generate_internal_number(db, request_data.project_name, request_data.deal_number)
    
    # Определение статуса
    if counterparty.status == CounterpartyStatus.APPROVED:
        req_status = RequestStatus.PENDING_DIRECTOR
    else:
        req_status = RequestStatus.PENDING_SECURITY
    
    request = Request(
        **request_data.model_dump(),
        internal_number=internal_number,
        status=req_status,
        created_by_id=current_profile.id
    )
    
    db.add(request)
    db.commit()
    db.refresh(request)
    
    # Запись в журнал
    journal_entry = JournalEntry(
        action="REQUEST_CREATED",
        description=f"Создана заявка {request.internal_number}",
        entity_type="request",
        entity_id=request.id,
        performed_by_id=current_profile.id
    )
    db.add(journal_entry)
    db.commit()
    
    return request


@router.get("/{request_id}", response_model=RequestResponse)
def get_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_profile: Profile = Depends(get_current_profile)
):
    """Получение заявки по ID"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    # Проверка прав доступа
    if current_profile.role == UserRole.ENGINEER and request.created_by_id != current_profile.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой заявке")
    
    return request


@router.put("/{request_id}/approve", response_model=RequestResponse)
def approve_request(
    request_id: int,
    approve: bool = True,
    db: Session = Depends(get_db),
    current_profile: Profile = Depends(require_role(UserRole.DIRECTOR, UserRole.ADMIN))
):
    """Согласование или отклонение заявки директором"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    # Проверка статуса контрагента
    counterparty = db.query(Counterparty).filter(Counterparty.id == request.counterparty_id).first()
    if counterparty.status != CounterpartyStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Контрагент должен быть одобрен отделом безопасности"
        )
    
    if approve:
        request.status = RequestStatus.APPROVED
        request.approved_by_id = current_profile.id
        request.approved_at = datetime.utcnow()
        action = "REQUEST_APPROVED"
        description = f"Заявка {request.internal_number} согласована"
    else:
        request.status = RequestStatus.REJECTED
        action = "REQUEST_REJECTED"
        description = f"Заявка {request.internal_number} отклонена"
    
    db.add(request)
    db.commit()
    db.refresh(request)
    
    # Запись в журнал
    journal_entry = JournalEntry(
        action=action,
        description=description,
        entity_type="request",
        entity_id=request.id,
        performed_by_id=current_profile.id
    )
    db.add(journal_entry)
    db.commit()
    
    return request


@router.put("/{request_id}/pay", response_model=RequestResponse)
def pay_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_profile: Profile = Depends(require_role(UserRole.ACCOUNTANT, UserRole.ADMIN))
):
    """Отметка об оплате (только бухгалтер)"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    if request.status != RequestStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно оплатить только согласованную заявку"
        )
    
    request.status = RequestStatus.PAID
    request.paid_at = datetime.utcnow()
    
    db.add(request)
    db.commit()
    db.refresh(request)
    
    # Запись в журнал
    journal_entry = JournalEntry(
        action="REQUEST_PAID",
        description=f"Заявка {request.internal_number} оплачена",
        entity_type="request",
        entity_id=request.id,
        performed_by_id=current_profile.id
    )
    db.add(journal_entry)
    db.commit()
    
    return request


@router.get("/{request_id}/pp-text")
def get_pp_text(
    request_id: int,
    db: Session = Depends(get_db),
    current_profile: Profile = Depends(get_current_profile)
):
    """Получение текста письма для бухгалтерии"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    # Проверка прав доступа
    if current_profile.role == UserRole.ENGINEER and request.created_by_id != current_profile.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой заявке")
    
    counterparty = db.query(Counterparty).filter(Counterparty.id == request.counterparty_id).first()
    
    text = f"""Здравствуйте!

Прошу оплатить счёт:

Номер счёта: {request.invoice_number}
Внутренний номер заявки: {request.internal_number}
Контрагент: {counterparty.name} (ИНН: {counterparty.inn})
Сумма: {request.amount or 'не указана'} руб.

Ссылка на файл счёта: {request.invoice_url}

С уважением,
{current_profile.full_name}
"""
    
    return {"text": text}

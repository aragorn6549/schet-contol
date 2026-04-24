from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import Profile
from app.models.journal import JournalEntry
from app.schemas.user import ProfileResponse, ProfileCreate
from app.core.dependencies import get_current_profile, require_admin
from app.core.enums import UserRole

router = APIRouter(prefix="/api/profiles", tags=["Профили"])


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(current_profile: Profile = Depends(get_current_profile)):
    """Получение своего профиля"""
    return current_profile


@router.get("/", response_model=List[ProfileResponse])
def get_all_profiles(
    skip: int = 0,
    limit: int = 100,
    current_profile: Profile = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Получение всех профилей (только админ)"""
    profiles = db.query(Profile).offset(skip).limit(limit).all()
    return profiles


@router.put("/{profile_id}", response_model=ProfileResponse)
def update_profile(
    profile_id: int,
    full_name: str = None,
    role: UserRole = None,
    current_profile: Profile = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Обновление профиля (только админ)"""
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    
    if full_name is not None:
        profile.full_name = full_name
    
    if role is not None:
        profile.role = role.value if isinstance(role, UserRole) else role
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    # Запись в журнал
    journal_entry = JournalEntry(
        action="PROFILE_UPDATED",
        description=f"Обновлён профиль {profile.full_name}",
        entity_type="profile",
        entity_id=profile.id,
        performed_by_id=current_profile.id
    )
    db.add(journal_entry)
    db.commit()
    
    return profile

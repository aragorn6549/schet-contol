from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, Profile
from app.models.journal import JournalEntry
from app.schemas.user import UserCreate, UserResponse, ProfileResponse, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.dependencies import get_current_user, get_current_profile
from app.core.enums import UserRole
from app.config import settings
from datetime import timedelta

router = APIRouter(prefix="/api/auth", tags=["Аутентификация"])


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    # Проверка существующего логина (только латиница и цифры)
    if not user_data.login.isalnum():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Логин должен содержать только латинские буквы и цифры"
        )
    
    existing_user = db.query(User).filter(User.login == user_data.login).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином уже существует"
        )
    
    # Создание пользователя
    user = User(
        login=user_data.login,
        password_hash=get_password_hash(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Создание профиля с ролью по умолчанию
    profile = Profile(
        user_id=user.id,
        full_name=user_data.login,  # Будет обновлён администратором
        role=UserRole.ENGINEER
    )
    db.add(profile)
    db.commit()
    
    # Запись в журнал
    journal_entry = JournalEntry(
        action="USER_REGISTERED",
        description=f"Зарегистрирован пользователь {user.login}",
        entity_type="user",
        entity_id=user.id,
        performed_by_id=profile.id
    )
    db.add(journal_entry)
    db.commit()
    
    return user


@router.post("/login", response_model=Token)
def login(login: str, password: str, db: Session = Depends(get_db)):
    """Вход в систему"""
    # Проверка формата логина
    if not login.isalnum():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Логин должен содержать только латинские буквы и цифры"
        )
    
    user = db.query(User).filter(User.login == login).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Учётная запись деактивирована"
        )
    
    access_token = create_access_token(
        data={"sub": user.login},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=ProfileResponse)
def get_me(current_profile: Profile = Depends(get_current_profile)):
    """Получение текущего профиля"""
    return current_profile

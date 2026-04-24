from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, profiles, counterparties, requests, journal
from app.config import settings
from app.core.security import get_password_hash
from app.models.user import User, Profile
from app.core.enums import UserRole
from app.database import engine, Base, SessionLocal


app = FastAPI(
    title=settings.APP_NAME,
    description="Система управления счетами и платежами",
    version="1.0.0"
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Создание таблиц БД и администратора при первом запуске"""
    # Создание таблиц
    Base.metadata.create_all(bind=engine)
    
    # Создание администратора при первом запуске
    db = SessionLocal()
    try:
        # Проверка существования админа
        admin_user = db.query(User).filter(User.login == settings.FIRST_ADMIN_LOGIN).first()
        
        if not admin_user:
            # Создание пользователя-администратора
            admin_user = User(
                login=settings.FIRST_ADMIN_LOGIN,
                password_hash=get_password_hash(settings.FIRST_ADMIN_PASSWORD),
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            # Создание профиля администратора
            admin_profile = Profile(
                user_id=admin_user.id,
                full_name=settings.FIRST_ADMIN_FULL_NAME,
                role=UserRole.ADMIN
            )
            db.add(admin_profile)
            db.commit()
            
            print(f"Администратор создан: {settings.FIRST_ADMIN_LOGIN} / {settings.FIRST_ADMIN_PASSWORD}")
    finally:
        db.close()


# Подключение роутов
app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(counterparties.router)
app.include_router(requests.router)
app.include_router(journal.router)


@app.get("/")
def root():
    return {"message": "СчетКонтроль API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

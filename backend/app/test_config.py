"""
Конфигурация для тестирования
"""
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    APP_NAME: str = "СчетКонтроль (Test)"
    DATABASE_URL: str = "sqlite:///:memory:"
    SECRET_KEY: str = "test-secret-key-for-testing-only"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FIRST_ADMIN_LOGIN: str = "admin"
    FIRST_ADMIN_PASSWORD: str = "admin123"
    FIRST_ADMIN_FULL_NAME: str = "Администратор Системы"


settings = TestSettings()

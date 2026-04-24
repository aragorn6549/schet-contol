import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Тестовая база данных в памяти (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


def create_test_app():
    """Создает тестовое приложение с SQLite in-memory БД"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    # Создаем тестовый движок и сессию
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Импортируем Base и модели для создания таблиц
    from app.database import Base
    from app.models import User, Profile, Counterparty, Request, JournalEntry
    
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)
    
    # Создаем приложение
    app = FastAPI(title="СчетКонтроль Тест", version="1.0.0")
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Переопределяем зависимость get_db
    def get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Импортируем роутеры
    from app.api import auth, profiles, counterparties, requests, journal
    
    # Подключаем роутеры с переопределенной зависимостью
    from app.database import get_db as original_get_db
    
    app.include_router(auth.router)
    app.include_router(profiles.router)
    app.include_router(counterparties.router)
    app.include_router(requests.router)
    app.include_router(journal.router)
    
    # Переопределяем зависимость для всех роутеров
    app.dependency_overrides[original_get_db] = get_db
    
    @app.get("/")
    def root():
        return {"message": "СчетКонтроль API", "version": "1.0.0"}
    
    @app.get("/health")
    def health_check():
        return {"status": "ok"}
    
    return app


@pytest.fixture(scope="function")
def client():
    """Создает тестовый клиент с изолированной SQLite БД"""
    app = create_test_app()
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


def test_root(client):
    """Тест главной страницы API"""
    response = client.get("/")
    assert response.status_code == 200


def test_register_user(client):
    """Тест регистрации пользователя"""
    response = client.post(
        "/api/auth/register",
        json={
            "login": "testuser",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["login"] == "testuser"
    assert "id" in data


def test_login_user(client):
    """Тест входа пользователя"""
    # Сначала регистрируем
    client.post(
        "/api/auth/register",
        json={
            "login": "loginuser",
            "password": "loginpass123"
        }
    )
    
    # Затем входим
    response = client.post(
        "/api/auth/login?login=loginuser&password=loginpass123"
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_wrong_password(client):
    """Тест входа с неправильным паролем"""
    # Регистрируем
    client.post(
        "/api/auth/register",
        json={
            "login": "wrongpassuser",
            "password": "correctpass123"
        }
    )
    
    # Пытаемся войти с неправильным паролем
    response = client.post(
        "/api/auth/login?login=wrongpassuser&password=wrongpass123"
    )
    assert response.status_code == 401


def test_create_counterparty(client):
    """Тест создания контрагента"""
    # Регистрируемся и получаем токен
    client.post(
        "/api/auth/register",
        json={
            "login": "cpuser",
            "password": "cppass123"
        }
    )
    login_response = client.post(
        "/api/auth/login?login=cpuser&password=cppass123"
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Создаем контрагента
    response = client.post(
        "/api/counterparties",
        headers=headers,
        json={
            "name": "ООО Тест",
            "inn": "7701234567",
            "kpp": "770101001",
            "ogrn": "1027700123456",
            "legal_address": "г. Москва, ул. Тестовая, д. 1",
            "bank_name": "ПАО Сбербанк",
            "bik": "044525225",
            "correspondent_account": "30101810400000000225",
            "checking_account": "40702810123456789012"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "ООО Тест"
    assert data["inn"] == "7701234567"
    assert data["status"] == "pending"


def test_get_counterparties(client):
    """Тест получения списка контрагентов"""
    # Регистрируемся
    client.post(
        "/api/auth/register",
        json={
            "login": "cpviewuser",
            "password": "cpviewpass123"
        }
    )
    login_response = client.post(
        "/api/auth/login?login=cpviewuser&password=cpviewpass123"
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Получаем список (должен быть пустым)
    response = client.get("/api/counterparties", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_request(client):
    """Тест создания заявки"""
    # Регистрируемся
    client.post(
        "/api/auth/register",
        json={
            "login": "requser",
            "password": "reqpass123"
        }
    )
    login_response = client.post(
        "/api/auth/login?login=requser&password=reqpass123"
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Создаем контрагента
    cp_response = client.post(
        "/api/counterparties",
        headers=headers,
        json={
            "name": "ООО Поставщик",
            "inn": "7709876543",
            "kpp": "770901001",
            "ogrn": "1027700987654",
            "legal_address": "г. Москва, ул. Поставочная, д. 5",
            "bank_name": "ВТБ",
            "bik": "044525187",
            "correspondent_account": "30101810700000000187",
            "checking_account": "40702810987654321098"
        }
    )
    counterparty_id = cp_response.json()["id"]
    
    # Создаем заявку
    response = client.post(
        "/api/requests",
        headers=headers,
        json={
            "project_name": "Проект Тест",
            "deal_number": "TEST-2024-001",
            "invoice_number": "INV-TEST-001",
            "invoice_url": "https://example.com/invoice.pdf",
            "counterparty_id": counterparty_id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["project_name"] == "Проект Тест"
    assert data["deal_number"] == "TEST-2024-001"
    assert "internal_number" in data


def test_get_requests_engineer(client):
    """Тест: инженер видит только свои заявки"""
    # Создаем первого инженера и заявку
    client.post(
        "/api/auth/register",
        json={
            "login": "engineer1",
            "password": "eng1pass123"
        }
    )
    login_response1 = client.post(
        "/api/auth/login?login=engineer1&password=eng1pass123"
    )
    token1 = login_response1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    # Создаем контрагента
    cp_response = client.post(
        "/api/counterparties",
        headers=headers1,
        json={
            "name": "ООО Для Теста",
            "inn": "7705555555",
            "kpp": "770501001",
            "ogrn": "1027700555555",
            "legal_address": "г. Москва",
            "bank_name": "Банк",
            "bik": "044525225",
            "correspondent_account": "30101810400000000225",
            "checking_account": "40702810111111111111"
        }
    )
    counterparty_id = cp_response.json()["id"]
    
    # Создаем заявку от первого инженера
    client.post(
        "/api/requests",
        headers=headers1,
        json={
            "project_name": "Проект 1",
            "deal_number": "PRJ1-001",
            "invoice_number": "INV-001",
            "invoice_url": "https://example.com/inv1.pdf",
            "counterparty_id": counterparty_id
        }
    )
    
    # Создаем второго инженера
    client.post(
        "/api/auth/register",
        json={
            "login": "engineer2",
            "password": "eng2pass123"
        }
    )
    login_response2 = client.post(
        "/api/auth/login?login=engineer2&password=eng2pass123"
    )
    token2 = login_response2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Второй инженер создает свою заявку
    client.post(
        "/api/requests",
        headers=headers2,
        json={
            "project_name": "Проект 2",
            "deal_number": "PRJ2-001",
            "invoice_number": "INV-002",
            "invoice_url": "https://example.com/inv2.pdf",
            "counterparty_id": counterparty_id
        }
    )
    
    # Первый инженер видит только свою заявку
    response = client.get("/api/requests", headers=headers1)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["project_name"] == "Проект 1"


def test_journal_entry_created(client):
    """Тест: создание записи в журнале при создании заявки"""
    # Регистрируемся
    client.post(
        "/api/auth/register",
        json={
            "login": "journaluser",
            "password": "jourpass123"
        }
    )
    login_response = client.post(
        "/api/auth/login?login=journaluser&password=jourpass123"
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Создаем контрагента
    cp_response = client.post(
        "/api/counterparties",
        headers=headers,
        json={
            "name": "ООО Журнал",
            "inn": "7704444444",
            "kpp": "770401001",
            "ogrn": "1027700444444",
            "legal_address": "г. Москва",
            "bank_name": "Банк",
            "bik": "044525225",
            "correspondent_account": "30101810400000000225",
            "checking_account": "40702810222222222222"
        }
    )
    counterparty_id = cp_response.json()["id"]
    
    # Создаем заявку
    client.post(
        "/api/requests",
        headers=headers,
        json={
            "project_name": "Проект Журнал",
            "deal_number": "JRN-001",
            "invoice_number": "INV-JRN-001",
            "invoice_url": "https://example.com/jrn.pdf",
            "counterparty_id": counterparty_id
        }
    )
    
    # Проверяем журнал
    response = client.get("/api/journal", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

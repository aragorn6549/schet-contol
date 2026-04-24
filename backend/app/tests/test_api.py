import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Тестовая база данных в памяти (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Создает тестовую сессию БД"""
    from app.database import Base
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Создает тестовый клиент с переопределенной БД"""
    # Импортируем app и get_db здесь, чтобы избежать проблем с инициализацией
    from app.main import app
    from app.database import get_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_root(client):
    """Тест главной страницы API"""
    response = client.get("/")
    assert response.status_code == 200


def test_register_user(client):
    """Тест регистрации пользователя"""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "password": "testpass123",
            "full_name": "Тест Пользователь"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_user(client, db_session):
    """Тест входа пользователя"""
    # Сначала регистрируем
    client.post(
        "/api/auth/register",
        json={
            "username": "loginuser",
            "password": "loginpass123",
            "full_name": "Логин Тест"
        }
    )
    
    # Затем входим
    response = client.post(
        "/api/auth/login",
        json={
            "username": "loginuser",
            "password": "loginpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_wrong_password(client, db_session):
    """Тест входа с неправильным паролем"""
    # Регистрируем
    client.post(
        "/api/auth/register",
        json={
            "username": "wrongpassuser",
            "password": "correctpass123",
            "full_name": "Wrong Pass Test"
        }
    )
    
    # Пытаемся войти с неправильным паролем
    response = client.post(
        "/api/auth/login",
        json={
            "username": "wrongpassuser",
            "password": "wrongpass123"
        }
    )
    assert response.status_code == 401


def test_create_counterparty(client, db_session):
    """Тест создания контрагента"""
    # Регистрируемся и получаем токен
    reg_response = client.post(
        "/api/auth/register",
        json={
            "username": "cpuser",
            "password": "cppass123",
            "full_name": "Counterparty User"
        }
    )
    token = reg_response.json()["access_token"]
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
    assert data["verification_status"] == "pending"


def test_get_counterparties(client, db_session):
    """Тест получения списка контрагентов"""
    # Регистрируемся
    reg_response = client.post(
        "/api/auth/register",
        json={
            "username": "cpviewuser",
            "password": "cpviewpass123",
            "full_name": "CP View User"
        }
    )
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Получаем список (должен быть пустым)
    response = client.get("/api/counterparties", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_request(client, db_session):
    """Тест создания заявки"""
    # Регистрируемся
    reg_response = client.post(
        "/api/auth/register",
        json={
            "username": "requser",
            "password": "reqpass123",
            "full_name": "Request User"
        }
    )
    token = reg_response.json()["access_token"]
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


def test_get_requests_engineer(client, db_session):
    """Тест: инженер видит только свои заявки"""
    # Создаем первого инженера и заявку
    reg1 = client.post(
        "/api/auth/register",
        json={
            "username": "engineer1",
            "password": "eng1pass123",
            "full_name": "Инженер 1"
        }
    )
    token1 = reg1.json()["access_token"]
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
    reg2 = client.post(
        "/api/auth/register",
        json={
            "username": "engineer2",
            "password": "eng2pass123",
            "full_name": "Инженер 2"
        }
    )
    token2 = reg2.json()["access_token"]
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


def test_journal_entry_created(client, db_session):
    """Тест: создание записи в журнале при создании заявки"""
    # Регистрируемся
    reg_response = client.post(
        "/api/auth/register",
        json={
            "username": "journaluser",
            "password": "jourpass123",
            "full_name": "Journal User"
        }
    )
    token = reg_response.json()["access_token"]
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

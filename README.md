# СчетКонтроль — Система управления счетами и платежами

## Описание
Корпоративная система для автоматизации полного цикла согласования и оплаты счетов.

## Технологический стек

### Бэкенд
- **Python 3.11+**
- **FastAPI** — REST API фреймворк
- **SQLAlchemy 2.0** — ORM
- **PostgreSQL** — база данных
- **Alembic** — миграции
- **PyJWT** — JWT токены
- **Passlib** — хеширование паролей
- **Pydantic** — валидация данных

### Фронтенд
- **React 18+**
- **TypeScript**
- **React Router** — навигация
- **React Query** — состояние сервера
- **TailwindCSS** — стили
- **Axios** — HTTP клиент

## Структура проекта

```
schetkontrol/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Точка входа FastAPI
│   │   ├── config.py            # Конфигурация
│   │   ├── database.py          # Подключение к БД
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # Модель пользователя
│   │   │   ├── profile.py       # Профиль с ролью
│   │   │   ├── counterparty.py  # Контрагенты
│   │   │   ├── request.py       # Заявки
│   │   │   └── journal.py       # Журнал действий
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # Pydantic схемы
│   │   │   ├── profile.py
│   │   │   ├── counterparty.py
│   │   │   ├── request.py
│   │   │   └── journal.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Аутентификация
│   │   │   ├── profiles.py      # Профили
│   │   │   ├── counterparties.py
│   │   │   ├── requests.py
│   │   │   └── journal.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py      # JWT, пароли
│   │   │   └── dependencies.py  # Зависимости
│   │   └── migrations/          # Alembic миграции
│   ├── requirements.txt
│   └── alembic.ini
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── types/
│   ├── package.json
│   └── tailwind.config.js
├── docker-compose.yml
└── README.md
```

## Роли пользователей

| Роль | Описание |
|------|----------|
| `engineer` | Создаёт заявки, видит только свои |
| `security` | Проверяет контрагентов |
| `director` | Согласовывает счета |
| `accountant` | Отмечает оплату |
| `admin` | Полный контроль |

## Статусы заявки

1. `draft` — черновик
2. `pending_security` — проверка контрагента
3. `pending_director` — ожидает директора
4. `approved` — согласован
5. `rejected` — отклонён
6. `paid` — оплачен
7. `counterparty_rejected` — контрагент отклонён

## Быстрый старт

### Требования
- Docker и Docker Compose
- Python 3.11+
- Node.js 18+

### Запуск

```bash
# Бэкенд
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Фронтенд
cd frontend
npm install
npm run dev
```

## API Endpoints

### Аутентификация
- `POST /api/auth/register` — регистрация
- `POST /api/auth/login` — вход
- `POST /api/auth/logout` — выход

### Профили
- `GET /api/profiles/me` — мой профиль
- `GET /api/profiles` — все профили (admin)
- `PUT /api/profiles/{id}` — обновление (admin)

### Контрагенты
- `GET /api/counterparties` — список
- `POST /api/counterparties` — создание
- `PUT /api/counterparties/{id}/status` — статус проверки (security)

### Заявки
- `GET /api/requests` — список (с фильтрацией по роли)
- `POST /api/requests` — создание
- `PUT /api/requests/{id}/approve` — согласование (director)
- `PUT /api/requests/{id}/pay` — оплата (accountant)

### Журнал
- `GET /api/journal` — история операций

## Лицензия
Внутренняя разработка

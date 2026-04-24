# Инструкция по деплою и тестированию СчетКонтроль

## 1. Деплой на Vercel (Фронтенд)

### Подготовка
```bash
cd frontend
npm install
```

### Вариант А: Через Vercel CLI
```bash
# Установить Vercel CLI
npm install -g vercel

# Войти в аккаунт
vercel login

# Деплой
vercel --prod
```

### Вариант Б: Через GitHub + Vercel Dashboard
1. Запушить код в GitHub репозиторий
2. Зайти на https://vercel.com
3. Import проект из GitHub
4. Настроить переменные окружения:
   - `VITE_API_URL` = URL вашего бэкенда
5. Нажать Deploy

### Настройка API прокси
В файле `frontend/vercel.json` замените `YOUR-BACKEND-URL` на реальный URL бэкенда.

---

## 2. Деплой Бэкенда

Так как Supabase недоступен в РФ, используем альтернативы:

### Вариант А: Render.com (рекомендуется)
1. Создать аккаунт на https://render.com
2. Создать PostgreSQL базу данных
3. Создать Web Service:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Добавить переменные окружения:
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

### Вариант Б: Railway.app
1. Создать аккаунт на https://railway.app
2. Создать PostgreSQL сервис
3. Deploy из GitHub репозитория
4. Настроить переменные окружения

### Вариант В: Собственный сервер (Docker)
```bash
# На сервере с Docker
docker-compose up -d
```

---

## 3. Локальное тестирование

### Запуск через Docker Compose
```bash
# В корне проекта
docker-compose up --build
```

Доступ:
- Фронтенд: http://localhost:5173
- Бэкенд: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Ручное тестирование API

#### 1. Регистрация администратора
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123",
    "full_name": "Администратор Системы"
  }'
```

#### 2. Вход в систему
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

#### 3. Создание контрагента
```bash
curl -X POST http://localhost:8000/api/counterparties \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "ООО Ромашка",
    "inn": "7701234567",
    "kpp": "770101001",
    "ogrn": "1027700123456",
    "legal_address": "г. Москва, ул. Примерная, д. 1",
    "bank_name": "ПАО Сбербанк",
    "bik": "044525225",
    "correspondent_account": "30101810400000000225",
    "checking_account": "40702810123456789012"
  }'
```

#### 4. Создание заявки
```bash
curl -X POST http://localhost:8000/api/requests \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "project_name": "Проект Альфа",
    "deal_number": "DA-2024-001",
    "invoice_number": "INV-123",
    "invoice_url": "https://example.com/invoice.pdf",
    "counterparty_id": 1
  }'
```

---

## 4. Автоматические тесты

### Backend тесты (pytest)
```bash
cd backend
pip install pytest pytest-asyncio httpx

# Запустить тесты
pytest
```

### Frontend тесты (Vitest)
```bash
cd frontend
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom

# Добавить в package.json:
# "test": "vitest"

npm run test
```

---

## 5. Проверка ролевой модели

| Роль | Логин/Пароль | Что проверять |
|------|-------------|---------------|
| Engineer | engineer/eng123 | Видит только свои заявки, создаёт новые |
| Security | security/sec123 | Проверяет контрагентов |
| Director | director/dir123 | Согласовывает счета |
| Accountant | accountant/acc123 | Отмечает оплату |
| Admin | admin/admin123 | Полный доступ, управление пользователями |

---

## 6. Переменные окружения

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

### Backend (.env)
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/schetkontrol
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 7. Чек-лист перед продакшеном

- [ ] Изменить SECRET_KEY на уникальный
- [ ] Настроить HTTPS
- [ ] Проверить CORS настройки
- [ ] Протестировать все роли
- [ ] Проверить журнал действий
- [ ] Сделать бэкап БД
- [ ] Настроить мониторинг

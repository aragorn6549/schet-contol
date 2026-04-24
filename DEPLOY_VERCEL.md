# Деплой на Vercel

## Предварительные требования

1. Учетная запись Vercel (https://vercel.com)
2. Проект Supabase настроен (см. SUPABASE_SETUP.md)
3. Файл `.env.local` с ключами Supabase в папке frontend

## Способ 1: Деплой через Vercel CLI (рекомендуется)

### Шаг 1: Установите Vercel CLI

```bash
npm install -g vercel
```

### Шаг 2: Войдите в Vercel

```bash
vercel login
```

Следуйте инструкциям для входа через браузер.

### Шаг 3: Перейдите в папку frontend

```bash
cd /workspace/frontend
```

### Шаг 4: Создайте проект Vercel

```bash
vercel
```

При первом запуске:
- Нажмите `Y` для продолжения
- Выберите `Set up and deploy`
- Дайте проекту имя (например, `schetkontrol`)
- Оставьте настройки по умолчанию

### Шаг 5: Добавьте переменные окружения

После первого деплоя добавьте переменные окружения:

```bash
vercel env add VITE_SUPABASE_URL production
vercel env add VITE_SUPABASE_ANON_KEY production
```

Введите значения из вашего `.env.local` файла.

Или добавьте их через веб-интерфейс:
1. Зайдите в проект на https://vercel.com/dashboard
2. Выберите ваш проект
3. Перейдите в Settings → Environment Variables
4. Добавьте `VITE_SUPABASE_URL` и `VITE_SUPABASE_ANON_KEY`

### Шаг 6: Задеплойте в production

```bash
vercel --prod
```

## Способ 2: Деплой через GitHub Integration

### Шаг 1: Запушьте код в GitHub

```bash
cd /workspace
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/schetkontrol.git
git push -u origin main
```

### Шаг 2: Подключите репозиторий к Vercel

1. Зайдите на https://vercel.com/new
2. Нажмите **Import Git Repository**
3. Выберите ваш репозиторий `schetkontrol`
4. В настройках проекта укажите:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### Шаг 3: Добавьте переменные окружения

В интерфейсе Vercel при создании проекта или после:
1. Перейдите в Settings → Environment Variables
2. Добавьте:
   - `VITE_SUPABASE_URL` = ваше значение
   - `VITE_SUPABASE_ANON_KEY` = ваше значение

### Шаг 4: Деплой

Нажмите **Deploy**. Vercel автоматически соберет и развернет проект.

## Проверка деплоя

После успешного деплоя:
1. Откройте URL вашего приложения (предоставляется Vercel)
2. Попробуйте войти под учетной записью администратора
3. Проверьте работу всех разделов

## Обновление проекта

Для обновления после изменений в коде:

```bash
cd /workspace/frontend
vercel --prod
```

Или просто запушьте изменения в GitHub (если используете интеграцию).

## Примечания

- Vercel автоматически предоставляет HTTPS
- Бесплатный тариф включает 100 ГБ трафика в месяц
- Для продакшена рекомендуется подключить собственный домен

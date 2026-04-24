# Настройка Supabase для проекта "СчетКонтроль"

## Шаг 1: Выполните SQL-скрипт в панели Supabase

1. Зайдите в ваш проект на https://supabase.com/dashboard
2. Перейдите в раздел **SQL Editor** (в левом меню)
3. Нажмите **New Query**
4. Скопируйте и выполните следующий SQL-код:

```sql
-- 1. Включаем расширения
create extension if not exists "uuid-ossp";

-- 2. Создаем типы (перечисления)
create type user_role as enum ('engineer', 'security', 'director', 'accountant', 'admin');
create type counterparty_status as enum ('pending', 'approved', 'rejected');
create type request_status as enum ('draft', 'pending_security', 'pending_director', 'approved', 'paid', 'rejected');

-- 3. Таблица профилей (расширяет auth.users)
create table profiles (
  id uuid references auth.users on delete cascade primary key,
  full_name text,
  role user_role default 'engineer',
  created_at timestamptz default now()
);

-- 4. Таблица контрагентов
create table counterparties (
  id uuid default uuid_generate_v4() primary key,
  inn varchar(20) unique not null,
  name text not null,
  legal_address text,
  bank_name text,
  bik varchar(20),
  account_number varchar(20),
  status counterparty_status default 'pending',
  created_by uuid references profiles(id),
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 5. Таблица заявок
create table requests (
  id uuid default uuid_generate_v4() primary key,
  internal_number text unique,
  project_name text not null,
  deal_number text not null,
  invoice_number text not null,
  invoice_url text not null,
  amount numeric,
  counterparty_id uuid references counterparties(id),
  created_by uuid references profiles(id),
  status request_status default 'draft',
  paid_at timestamptz,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 6. Журнал действий
create table journal (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references profiles(id),
  action text not null,
  details jsonb,
  created_at timestamptz default now()
);

-- 7. Триггер для создания профиля при регистрации
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, full_name, role)
  values (new.id, new.raw_user_meta_data->>'full_name', 'engineer');
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- 8. Функция для генерации внутреннего номера заявки
create or replace function generate_internal_number(proj_name text, deal_num text)
returns text as $$
declare
  seq_num integer;
begin
  select count(*) + 1 into seq_num from requests where project_name = proj_name and deal_number = deal_num;
  return proj_name || '_' || deal_num || '_' || lpad(seq_num::text, 3, '0');
end;
$$ language plpgsql;

-- 9. RLS (Row Level Security) - ВКЛЮЧАЕМ ЗАЩИТУ
alter table profiles enable row level security;
alter table counterparties enable row level security;
alter table requests enable row level security;
alter table journal enable row level security;

-- ПОЛИТИКИ ДЛЯ profiles
create policy "Public read own profile" on profiles for select using (auth.uid() = id);
create policy "Admin read all profiles" on profiles for select using (exists (select 1 from profiles where id = auth.uid() and role = 'admin'));
create policy "Admin update profiles" on profiles for update using (exists (select 1 from profiles where id = auth.uid() and role = 'admin'));

-- ПОЛИТИКИ ДЛЯ counterparties
create policy "Auth users read counterparties" on counterparties for select using (auth.role() = 'authenticated');
create policy "Auth users create counterparties" on counterparties for insert with check (auth.role() = 'authenticated');
create policy "Security/Admin update counterparties" on counterparties for update 
  using (exists (select 1 from profiles where id = auth.uid() and role in ('security', 'admin')));

-- ПОЛИТИКИ ДЛЯ requests
create policy "Engineers read own requests" on requests for select 
  using (auth.uid() = created_by OR exists (select 1 from profiles where id = auth.uid() and role in ('director', 'admin')));
create policy "Engineers create requests" on requests for insert 
  with check (auth.uid() = created_by);
create policy "Directors update requests" on requests for update 
  using (exists (select 1 from profiles where id = auth.uid() and role in ('director', 'admin', 'accountant')));

-- ПОЛИТИКИ ДЛЯ journal
create policy "Auth users read journal" on journal for select using (auth.role() = 'authenticated');
create policy "Auth users insert journal" on journal for insert with check (auth.uid() = user_id);
```

## Шаг 2: Отключите подтверждение email

1. В панели Supabase перейдите в **Authentication** → **Providers** → **Email**
2. Отключите опцию **"Confirm email"**
3. Сохраните изменения

## Шаг 3: Создайте первого администратора

В том же SQL Editor выполните:

```sql
-- Замените email и пароль на ваши!
DO $$
DECLARE
  admin_id uuid;
BEGIN
  -- Создаем пользователя
  INSERT INTO auth.users (
    instance_id, id, aud, role, email, encrypted_password, 
    email_confirmed_at, raw_app_meta_data, raw_user_meta_data, 
    created_at, updated_at
  )
  SELECT 
    '00000000-0000-0000-0000-000000000000',
    uuid_generate_v4(),
    'authenticated',
    'authenticated',
    'admin@yourcompany.com', -- ЗАМЕНИТЕ НА ВАШ EMAIL
    crypt('YourSecurePassword123', gen_salt('bf')), -- ЗАМЕНИТЕ НА ВАШ ПАРОЛЬ
    now(),
    '{"provider":"email","providers":["email"]}',
    '{"full_name":"System Administrator"}',
    now(),
    now()
  WHERE NOT EXISTS (SELECT 1 FROM auth.users WHERE email = 'admin@yourcompany.com')
  RETURNING id INTO admin_id;
  
  -- Назначаем роль админа
  IF admin_id IS NOT NULL THEN
    UPDATE profiles SET role = 'admin' WHERE id = admin_id;
  END IF;
END $$;
```

## Шаг 4: Настройте переменные окружения

1. В панели Supabase перейдите в **Settings** → **API**
2. Скопируйте:
   - **Project URL** (например, `https://xxxxx.supabase.co`)
   - **anon public** ключ (начинается с `eyJ...`)

3. В корне проекта frontend создайте файл `.env.local`:

```bash
cd /workspace/frontend
cp .env.example .env.local
```

4. Отредактируйте `.env.local` и вставьте ваши ключи:

```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

## Шаг 5: Установите зависимости и запустите проект

```bash
cd /workspace/frontend
npm install
npm run dev
```

## Готово!

Теперь вы можете войти в систему под учетной записью администратора, которую создали в Шаге 3.

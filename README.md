# SB1 Market API

![CI/CD](https://github.com/BrailaVasilii/SB1-market-api/workflows/CI%2FCD%20Pipeline/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Django](https://img.shields.io/badge/django-5.2-green.svg)
![Coverage](https://img.shields.io/badge/coverage-76%25-brightgreen.svg)
![Tests](https://img.shields.io/badge/tests-36%20passed-success.svg)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)

Backend API для доски объявлений (дипломный проект).

## 📋 Описание

REST API для платформы объявлений с функционалом управления пользователями, объявлениями и отзывами.

### Основные возможности:
- 👤 Управление пользователями (регистрация, авторизация, профиль)
- 📝 CRUD операции для объявлений
- 💬 Система отзывов
- 🔐 JWT авторизация
- 🔑 Сброс пароля через email
- 🔍 Поиск объявлений по названию
- 📄 Пагинация (4 объявления на страницу)
- 👮 Разграничение прав доступа (User, Admin)

## 🛠 Технологии

- **Python 3.12**
- **Django 5.2.8**
- **Django REST Framework 3.16.1**
- **PostgreSQL** (production) / SQLite (development)
- **Poetry** (управление зависимостями)
- **Docker & Docker Compose**
- **Celery + Redis** (асинхронные задачи)
- **pytest** (тестирование)

### Основные библиотеки:
- `djangorestframework-simplejwt` - JWT авторизация
- `djoser` - сброс пароля через email
- `django-filter` - фильтрация и поиск
- `django-cors-headers` - CORS поддержка
- `drf-spectacular` - OpenAPI документация

## 🚀 Установка и запуск

### Локальная разработка (SQLite)
```bash
# Клонировать репозиторий
git clone https://github.com/BrailaVasilii/SB1-market-api.git
cd SB1-market-api

# Установить зависимости
poetry install

# Создать .env файл
cp .env.example .env

# Применить миграции
poetry run python manage.py migrate

# Создать суперпользователя
poetry run python manage.py createsuperuser

# Запустить сервер
poetry run python manage.py runserver
```

API будет доступен по адресу: http://localhost:8000

### Docker (Production-ready)
```bash
# Запустить все сервисы
docker-compose up -d

# Применить миграции
docker-compose exec web python manage.py migrate

# Создать суперпользователя
docker-compose exec web python manage.py createsuperuser
```

API будет доступен по адресу: http://localhost:8000

## 📚 API Документация

После запуска сервера документация доступна:
- **Swagger UI**: http://localhost:8000/api/docs/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 🔑 Основные эндпоинты

### Авторизация
- `POST /api/token/` - Получить JWT токен
- `POST /api/token/refresh/` - Обновить токен
- `POST /api/auth/users/reset_password/` - Запрос на сброс пароля
- `POST /api/auth/users/reset_password_confirm/` - Подтверждение сброса пароля

### Объявления
- `GET /api/ads/` - Список объявлений (пагинация, поиск)
- `POST /api/ads/` - Создать объявление (auth required)
- `GET /api/ads/{id}/` - Детали объявления
- `PATCH /api/ads/{id}/` - Обновить объявление (owner/admin)
- `DELETE /api/ads/{id}/` - Удалить объявление (owner/admin)

### Отзывы
- `GET /api/reviews/` - Список отзывов
- `POST /api/reviews/` - Создать отзыв (auth required)
- `PATCH /api/reviews/{id}/` - Обновить отзыв (owner/admin)
- `DELETE /api/reviews/{id}/` - Удалить отзыв (owner/admin)

## 🔒 Права доступа

### Анонимный пользователь
- ✅ Просмотр списка объявлений
- ✅ Просмотр деталей объявления
- ❌ Создание, редактирование, удаление

### Авторизованный пользователь (User)
- ✅ Всё что анонимный
- ✅ Создание объявлений и отзывов
- ✅ Редактирование/удаление своих объявлений и отзывов
- ❌ Редактирование/удаление чужих объявлений

### Администратор (Admin)
- ✅ Всё что пользователь
- ✅ Редактирование/удаление любых объявлений и отзывов

## 🧪 Тестирование
```bash
# Запустить все тесты
poetry run pytest

# Запустить с coverage
poetry run pytest --cov=. --cov-report=html

# Просмотр coverage report
open htmlcov/index.html
```

## 📁 Структура проекта

```
SB1-market-api/
├── config/              # Django настройки и конфигурация
├── users/               # Приложение пользователей
├── materials/           # Приложение объявлений и отзывов
├── tests/               # Тесты
├── .env.example         # Пример файла окружения
├── docker-compose.yml   # Docker конфигурация
├── Dockerfile           # Docker образ
├── pyproject.toml       # Poetry зависимости
└── manage.py            # Django management script
```

## 🗃️ Модели данных

### User
- `email` - Email (используется как username)
- `first_name`, `last_name` - Имя и фамилия
- `phone` - Телефон
- `role` - Роль (user/admin)
- `avatar` - Аватар

### Advertisement
- `title` - Название товара
- `price` - Цена (целое число)
- `description` - Описание
- `author` - Автор объявления
- `image` - Изображение товара
- `created_at` - Дата создания

### Review
- `text` - Текст отзыва
- `author` - Автор отзыва
- `ad` - Объявление
- `created_at` - Дата создания

## 🔧 Переменные окружения

Основные переменные в `.env`:
```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=sb1_market_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
```

## 📝 Git workflow

Проект использует Git Flow с Pull Requests:
- `main` - production ready код
- `develop` - development ветка
- `feature/*` - ветки для новых фичей

## 👨‍💻 Автор

**Vasili Braila**
- Email: vbraila@gmail.com
- GitHub: [@BrailaVasilii](https://github.com/BrailaVasilii)

## 📄 Лицензия

Дипломный проект SB1.

---

**Дата создания**: Ноябрь 2024
**Версия**: 1.0.0

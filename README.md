# 🍇 Wine Library API

RESTful API for managing a wine collection, user reviews, and favorites.
Built with Django, Django REST Framework, PostgreSQL, and Swagger docs.

---

## ✨ Features

* User authentication and registration
* Wine CRUD (admin only)
* Review wines (one per user per wine)
* Save/unsave wines to favorites
* Filter wines by multiple parameters
* Upload wine images
* Swagger UI docs (Browsable)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/kkkkkkkkatya/wine_library.git
cd wine_library
```

### 2. Create Virtual Environment & Activate

```bash
python -m venv venv
source venv/bin/activate  # on Windows: .\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` File

Create a `.env` file in the root directory based on the template below.
Or just copy the existing template:

```bash
cp .env.example .env
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit: [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs) — Swagger UI

---

## 🐳 Запуск через Docker
Щоб швидко розгорнути проєкт у контейнерах Docker (Django + PostgreSQL), виконай наступні кроки:

1. Склонуй репозиторій (якщо ще не зробив)

```bash
git clone https://github.com/kkkkkkkkatya/wine_library.git
cd wine_library
```
2. Створи файл .env у корені проєкту на основі шаблону .env.sample
Переконайся, що в .env прописані змінні для БД, наприклад:


    POSTGRES_DB=wine_library
    POSTGRES_USER=wine_library
    POSTGRES_PASSWORD=wine1234
    POSTGRES_HOST=db
    POSTGRES_DB_PORT=5432
    SECRET_KEY=your-secret-key
    DEBUG=True
3. Запусти Docker Compose

```bash
docker compose up --build
```
Ця команда:

Збудує Docker-образи

Запустить контейнери для Django і PostgreSQL

Прив’яже порти (зазвичай 8000 для Django, 5432 для БД)

4. Створи суперкористувача (адміна)
```bash
docker compose exec web python manage.py createsuperuser
```
5. Відкрий браузер і перейди за адресою
```bash
http://localhost:8000/api/doc/swagger/
```
Там буде доступна Swagger UI документація.

Для зупинки та видалення контейнерів
```bash
docker compose down
```


## 🔧 Run Tests

Tests will use a separate temporary database and will not affect your main DB.

```bash
pytest
```

---

## 📂 .env.sample

```dotenv
# Django settings
SECRET_KEY=your-secret-key
DEBUG=True

# Database
POSTGRES_DB=wine_library
POSTGRES_DB_PORT=5432
POSTGRES_USER=wine_library
POSTGRES_PASSWORD=wine1234
POSTGRES_HOST=127.0.0.1
PGDATA=/var/lib/postgresql/data
```

---

## 🚧 Tech Stack

* Django & DRF
* PostgreSQL
* Pillow (for image handling)
* drf-spectacular (for OpenAPI docs)
* Docker (optional)

---

## 🎓 API Docs

Interactive Swagger docs available at:

```
http://127.0.0.1:8000/api/docs/
```

---



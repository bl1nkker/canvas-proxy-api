# Canvas Proxy with Face Recognition

## 🚀 Usage

### ✅ Enable Custom Git Hooks

Configure Git to use the custom hooks:

```sh
git config core.hooksPath .githooks

# Or using Makefile
make enable-git-hooks
```

### 🐳 Install and Run Docker Services

Start all necessary services using Docker:

```sh
cd deployment/local && ./up.sh
```

### 📦 Install Dependencies with Poetry

Make sure dependencies are installed:

```sh
cd app && poetry install --no-root
```

### 🏗️ Initialize Database

Set up the database schema:

```sh
cd app && poetry run cli dbinit
```

### 📜 Apply Alembic Migrations

Run database migrations:

```sh
cd app && poetry run alembic upgrade head
```

### 🚀 Start API Server

Run the API server:

```sh
cd app/web && poetry run python api.py

# Or using Makefile
make start
```

### ⚙️ Start Celery Workers

Run background workers for async tasks:

```sh
# Celery Beat (Periodic Tasks)
cd app && poetry run celery -A celery_app beat --loglevel=info

# Celery Worker
cd app && poetry run celery -A celery_app worker --loglevel=info
```

## 🛠 Extra Commands

### ✅ Run Tests

Execute unit tests:

```sh
cd app && poetry run pytest
```

### 🔍 Run Linter

Check code quality:

```sh
cd app && poetry run ruff check .
```

### 🎨 Format Code

Auto-format the codebase:

```sh
cd app && poetry run ruff format .
```

### 🛑 Stop Docker Services

Shut down running containers:

```sh
cd deployment/local && ./down.sh
```

### 🏗️ Initialize/Drop Test Database

Set up or remove the test database:

```sh
cd app && PYTHON_ENV=test poetry run cli dbinit
cd app && PYTHON_ENV=test poetry run cli dbdrop
```

### 📜 Apply Alembic Migrations for Test Environment

Run migrations in test mode:

```sh
cd app && PYTHON_ENV=test poetry run alembic upgrade head
```

### 📝 Create a New Alembic Migration

Generate a new migration script:

```sh
cd app && poetry run alembic revision --autogenerate -m "<message>"
```

## 📝 TODOs

- Improve ML for face recognition (FAISS, HNSW)
- Add HNSW index (as default?)
- Improve user existence check in Canvas
- Add tests for Canvas-related functionality (wait-for-it)

### ⚠️ TEST EVERYTHING

- Courses
- Students
- Enrollments
- Attendance

---

If you have any issues or improvements, feel free to contribute! 🚀

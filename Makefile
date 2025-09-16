# ======================
# 🔧 Настройки
# ======================
DOCKER_COMPOSE = docker-compose
DB_USER = postgres
DB_NAME = mydb
DB_PORT = 54321

# ======================
# 🚀 DEV (локально)
# ======================
dev:
	@echo "👉 Запуск Flask в debug режиме (localhost:8081)"
	FLASK_ENV=development flask run --host=0.0.0.0 --port=8081

dev-install:
	@echo "👉 Установка зависимостей в venv"
	python -m venv venv && \
	. venv/bin/activate && \
	pip install -r requirements.txt

dev-db-up:
	@echo "👉 Запуск только PostgreSQL (dev)"
	$(DOCKER_COMPOSE) up -d postgres
	@echo "⏳ Ожидаем запуск Postgres..."
	sleep 5
	make psql || true

# ======================
# 🐳 PROD (Docker)
# ======================
prod:
	@echo "👉 Запуск Docker (production mode)"
	$(DOCKER_COMPOSE) up -d

prod-build:
	@echo "👉 Пересборка и запуск Docker"
	$(DOCKER_COMPOSE) up -d --build

prod-logs:
	@echo "👉 Логи Flask (uwsgi)"
	$(DOCKER_COMPOSE) logs -f flask

# ======================
# 🗄️ База данных
# ======================
psql:
	@echo "👉 Подключение к БД через psql (localhost:$(DB_PORT))"
	psql -h localhost -p $(DB_PORT) -U $(DB_USER) -d $(DB_NAME)

db-reset:
	@echo "👉 Полный сброс БД"
	$(DOCKER_COMPOSE) down -v
	$(DOCKER_COMPOSE) up -d

# ======================
# 🧹 Утилиты
# ======================
stop:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

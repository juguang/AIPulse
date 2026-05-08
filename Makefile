.PHONY: dev dev-api dev-frontend db-start db-stop db-reset lint format

# 一键启动所有服务（需要先启动数据库）
dev: dev-api dev-frontend

# 启动 FastAPI 后端（热重载）
dev-api:
	uv run uvicorn app.main:app --reload --port 8000

# 启动 React 前端
dev-frontend:
	cd frontend && pnpm dev

# 启动 PostgreSQL（Homebrew）
db-start:
	brew services start postgresql@16

# 停止 PostgreSQL
db-stop:
	brew services stop postgresql@16

# 创建数据库
db-create:
	createdb aihot

# 重置数据库
db-reset:
	dropdb aihot; createdb aihot; uv run alembic upgrade head

# 运行数据库迁移
migrate:
	uv run alembic upgrade head

# 生成新的迁移
migrate-new:
	uv run alembic revision --autogenerate -m "$(msg)"

# 安装后端依赖
install:
	uv sync

# 安装前端依赖
install-frontend:
	cd frontend && pnpm install

# 代码检查
lint:
	cd frontend && pnpm lint

# 代码格式化
format:
	cd frontend && pnpm prettier --write src/

# 查看提交历史
log:
	git log --oneline --graph -20

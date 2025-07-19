from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from pathlib import Path

# ==== 1. 경로 설정 및 .env 로드 ====

# 프로젝트 루트 기준: blog/.env
ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT_DIR / ".env"

from dotenv import load_dotenv
load_dotenv(dotenv_path=ENV_PATH)

# DATABASE_URL 환경변수 불러오기
DATABASE_URL = os.getenv("ALEMBIC_DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(f"❌ DATABASE_URL not found in {ENV_PATH}")

# ==== 2. sys.path 설정 및 Base 불러오기 ====

# src 폴더를 sys.path에 추가 (FastAPI app 경로)
SRC_PATH = str(ROOT_DIR / "src")
sys.path.append(SRC_PATH)

# models에 정의된 Base metadata import
from database.orm import Base  # e.g., src/database/orm.py

# ==== 3. Alembic config 설정 ====

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# 로그 설정
if config.config_file_name:
    fileConfig(config.config_file_name)

# metadata 설정
target_metadata = Base.metadata

# ==== 4. 마이그레이션 실행 함수 ====

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

# ==== 5. 모드에 따라 실행 분기 ====

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

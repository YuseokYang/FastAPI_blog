from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from pathlib import Path

# ==== 1. 경로 설정 및 .env.dev / .env.prod 분기 ====

ROOT_DIR = Path(__file__).resolve().parents[2]

# ENV 값에 따라 분기 (기본은 dev)
ENV_MODE = os.getenv("ENV", "dev")  # 환경변수 ENV가 없으면 "dev"로 기본값 설정
ENV_FILE = ".env.prod" if ENV_MODE == "prod" else ".env.dev"
ENV_PATH = ROOT_DIR / ENV_FILE

from dotenv import load_dotenv
load_dotenv(dotenv_path=ENV_PATH)

# ✅ Alembic은 비동기용 DATABASE_URL이 아닌, 동기용 ALEMBIC_DATABASE_URL 사용
DATABASE_URL = os.getenv("ALEMBIC_DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(f"❌ ALEMBIC_DATABASE_URL not found in {ENV_FILE}")

# ==== 2. src 폴더 및 Base metadata 설정 ====

SRC_PATH = str(ROOT_DIR / "src")
sys.path.append(SRC_PATH)

from database.orm import Base  # Base.metadata를 불러오기 위한 경로
from database.orm import User
from database.orm import Post
from database.orm import Comment

# ==== 3. Alembic 설정 ====

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name:
    fileConfig(config.config_file_name)

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

# ==== 5. 실행 ====

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

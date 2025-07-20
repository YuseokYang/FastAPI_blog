from pydantic import BaseSettings
from dotenv import load_dotenv
import os

# 기본은 .env.dev
env_file = ".env.dev" if os.getenv("ENV") != "prod" else ".env.prod"
load_dotenv(dotenv_path=env_file)

class Settings(BaseSettings):
    DATABASE_URL: str
    ENV: str = "dev"  # 기본값 dev

settings = Settings()

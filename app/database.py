from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

#СТрока подключения для SQLite
DATABASE_URL = "sqlite:///ecommerce.db"

#Создаем engine
engine = create_engine(DATABASE_URL, echo=True)

# Настраивеам фабрику сеансов
SessionLocal = sessionmaker(bind=engine)

# --------------- Асинхронное подключение к PostgreSQL -------------------------
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "postgresql+asyncpg://postgres:Tema08978675@localhost:5432/ecommerce_db"

# Создаем Engine
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Настраиваем фабрику сеансов
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass
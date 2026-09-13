from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

#СТрока подключения для SQLite
DATABASE_URL = "sqlite:///ecommerce.db"

#Создаем engine
engine = create_engine(DATABASE_URL, echo=True)

# Настраивеам фабрику сеансов
SessionLocal = sessionmaker(bind=engine)

# Определяем базовый класс для моделей
class Base(DeclarativeBase):
    pass
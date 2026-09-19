from sqlalchemy.orm import Session
from collections.abc import Generator

from app.database import SessionLocal # Фабрика сессий

def get_db() -> Generator[Session, None, None]:
    """
    Зависимость для получения сессии базы данных
    Создает новую сессию для каждого запроса и закрывает её после обработки
    """

    db: Session = SessionLocal() # Создает новые сессии для работы с бд
    try:
        yield db #возвращает сессию
    finally:
        db.close()

# --------------- Асинхронная сессия -------------------------

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Предоставляет асинхронную сессию SQLAlchemy для работы с бд"""
    async with async_session_maker() as session:
        yield session  
from fastapi import APIRouter, FastAPI

router = APIRouter(
    prefix = "/categories", #Строка, добавляемая к началу всех маршрутов (например, /categories).
    tags = ["categories"], #Список строк для группировки эндпоинтов в документации.
)

@router.get("/")
async def get_all_categories():
    """Возвращает список всех категорий товаров"""
    return {"message": "Список всех категорий (заглушка)"}

@router.post("/")
async def create_category():
    """Создает новую категорию"""
    return {"message": "Категория создана (заглушка)"}

@router.put("/{category_id}")
async def update_category(category_id: int):
    """Обновляет категорию по её id"""
    return {"message": f"Категория с Id: {category_id} обновлена"}

@router.delete("/{category_id}")
async def delete_category(category_id: int):
    """Удаляет категорию по Id"""
    return  {"message": f"Категорию c ID {category_id} удалена"}
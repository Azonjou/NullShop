from fastapi import FastAPI
from app.routers import categories
from app.routers import products
from app.routers import users
from app.routers import reviews

#Создаем приложение FastAPI
app = FastAPI(
    title="FastAPI Интернет-магазин"
)

#Подключаем маршруты категорий
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(reviews.router)

#Корневой эндпоинт для проверки
@app.get("/")
async def root():
    """Корневой маршрут, подтверждающий, что API работает"""
    return {"message": "Добро подаловать в API интернет-магазин"}
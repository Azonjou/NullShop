from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.categories import Product as ProductModel
from app.schemas import Product as ProductShema, ProductCreate
from app.models.categories import Category as CategoryModel
from app.db_depends import get_db

#Создаем маршрутизатор для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"],
)

@router.get("/")
async def get_all_products():
    """Возвращаем список всех товаров"""
    return {"message": "Список всех товаров"}

@router.post("/", response_model=ProductShema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Создает новый товар"""
    status_category = select(CategoryModel.is_active).where(
        CategoryModel.id == product.category_id
    )

    stmt = db.scalars(status_category).first()
    if not stmt:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")

    db_product = CategoryModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/category/{category_id}")
async def get_products_by_category(category_id: int):
    """Возвращает список товаров в указанной категории по её ID"""
    return {"message": f"Товары в категории {category_id}"}

@router.get("/{product_id}")
async def get_product(product_id: int):
    """Возвращает детальную информацию о товаре по его ID"""
    return {"message": f"Детали товара {product_id}"}

@router.put("/{product_id}")
async def update_product(product_id: int):
    """Обновляет товар по его ID"""
    return {"message": f"Товар {product_id} обновлен"}

@router.delete("/{product_id}")
async def delete_product(product_id: int):
    """Удаляет товар по его ID"""
    return {"message": f"Товар {product_id} удален"}
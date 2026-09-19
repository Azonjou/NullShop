from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.products import Product as ProductModel
from app.schemas import Product as ProductShema, ProductCreate
from app.models.categories import Category as CategoryModel
from app.db_depends import get_db

#Создаем маршрутизатор для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"],
)

@router.get("/", response_model=list[ProductShema], status_code=status.HTTP_200_OK)
async def get_all_products(db: Session = Depends(get_db)):
    """Возвращаем список всех товаров"""
    stmt = select(ProductModel).join(CategoryModel).where(
        ProductModel.is_active == True,
        CategoryModel.is_active == True,
        ProductModel.stock > 0
    )
    products = db.scalars(stmt).all()
    return products

@router.post("/", response_model=ProductShema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Создает новый товар"""
    if product.category_id is not None:
        status_category = select(CategoryModel).where(
            CategoryModel.id == product.category_id,
            CategoryModel.is_active == True
        )

        stmt = db.scalars(status_category).first()

        if stmt is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Category not found or inactive")

    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/category/{category_id}", response_model=list[ProductShema], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    """Возвращает список товаров в указанной категории по её ID"""
    status_category = select(CategoryModel).where(
        CategoryModel.id == category_id,
        CategoryModel.is_active == True
    )

    stmt = db.scalars(status_category).first()

    if stmt is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Category not found or inactive")

    stmt_product = select(ProductModel).where(ProductModel.is_active == True, ProductModel.category_id == category_id)
    db_product = db.scalars(stmt_product).all()
    return db_product

@router.get("/{product_id}", response_model=ProductShema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Возвращает детальную информацию о товаре по его ID"""
    status_product = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active == True
    )

    db_product = db.scalars(status_product).first()

    if db_product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    status_category = select(CategoryModel).where(
        CategoryModel.id == db_product.category_id,
        CategoryModel.is_active == True
    )

    stmt = db.scalars(status_category).first()

    if stmt is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Category not found or inactive")

    return db_product

@router.put("/{product_id}", response_model=ProductShema, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    """Обновляет товар по его ID"""
    put_status_product = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active == True
    )

    db_product = db.scalars(put_status_product).first()

    if db_product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    if product.category_id is not None:
        status_category = select(CategoryModel).where(
            CategoryModel.id == product.category_id,
            CategoryModel.is_active == True
        )
        stmt = db.scalars(status_category).first()

        if stmt is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")

    db.execute(
        update(ProductModel).where(
            ProductModel.id == product_id
        ).values(**product.model_dump())
    )
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Удаляет товар по его ID"""
    stmt = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active == True
    )
    db_product = db.scalars(stmt).first()

    if db_product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    db_product.is_active = False
    db.commit()

    return {"status": "success", "message": "Product marked as inactive"}
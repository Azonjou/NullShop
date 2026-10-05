from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST

from app.auth import get_current_seller

from app.models.products import Product as ProductModel
from app.schemas import Product as ProductShema, ProductCreate

from app.models.categories import Category as CategoryModel

from app.models.reviews import Review as ReviewModel
from app.schemas import Review as ReviewShema, ReviewCreate

from app.db_depends import get_async_db

from app.models.users import User as UserModel
from app.auth import get_current_seller

#Создаем маршрутизатор для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"],
)

@router.get("/", response_model=list[ProductShema], status_code=status.HTTP_200_OK)
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    """Возвращаем список всех товаров"""
    stmt = await db.scalars(
        select(ProductModel).join(CategoryModel).where(
            ProductModel.is_active == True,
            CategoryModel.is_active == True,
            ProductModel.stock > 0
        )
    )
    products = stmt.all()
    return products

@router.post("/", response_model=ProductShema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_async_db), current_user: UserModel = Depends(get_current_seller)):
    """Создает новый товар"""
    if product.category_id is not None:
        status_category = select(CategoryModel).where(
            CategoryModel.id == product.category_id,
            CategoryModel.is_active == True
        )
        result = await db.scalars(status_category)
        stmt = result.first()

        if stmt is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Category not found or inactive")

    db_product = ProductModel(**product.model_dump(), seller_id=current_user.id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.get("/category/{category_id}", response_model=list[ProductShema], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """Возвращает список товаров в указанной категории по её ID"""
    status_category = select(CategoryModel).where(
        CategoryModel.id == category_id,
        CategoryModel.is_active == True
    )
    result = await db.scalars(status_category)
    stmt = result.first()

    if stmt is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Category not found or inactive")

    stmt_product = select(ProductModel).where(ProductModel.is_active == True, ProductModel.category_id == category_id)
    result_st = await db.scalars(stmt_product)
    db_product = result_st.all()
    return db_product

@router.get("/{product_id}", response_model=ProductShema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """Возвращает детальную информацию о товаре по его ID"""
    status_product = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active == True
    )

    result = await db.scalars(status_product)
    db_product = result.first()

    if db_product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    status_category = select(CategoryModel).where(
        CategoryModel.id == db_product.category_id,
        CategoryModel.is_active == True
    )

    result_st = await db.scalars(status_category)
    stmt = result_st.first()

    if stmt is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Category not found or inactive")

    return db_product

@router.put("/{product_id}", response_model=ProductShema, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product: ProductCreate, db: AsyncSession = Depends(get_async_db), current_user: UserModel = Depends(get_current_seller)):
    """Обновляет товар по его ID"""
    put_status_product = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active == True
    )

    result = await db.scalars(put_status_product)
    db_product = result.first()

    if db_product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")
    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own products")

    if product.category_id is not None:
        status_category = select(CategoryModel).where(
            CategoryModel.id == product.category_id,
            CategoryModel.is_active == True
        )

        result_st = await db.scalars(status_category)
        stmt = result_st.first()

        if stmt is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")

    update_data = product.model_dump(exclude_unset=True)
    await db.execute(
        update(ProductModel).where(
            ProductModel.id == product_id
        ).values(**update_data)
    )
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_async_db), current_user: UserModel = Depends(get_current_seller)):
    """Удаляет товар по его ID"""
    stmt = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active == True
    )
    result = await db.scalars(stmt)
    db_product = result.first()

    if db_product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")
    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own products")

    await db.execute(
        update(ProductModel).where(
            ProductModel.id == product_id
        ).values(is_active=False)
    )
    await db.commit()
    await db.refresh(db_product)
    return {"status": "success", "message": "Product marked as inactive"}

#Экзамен
@router.get("/{product_id}/reviews", response_model=list[ReviewShema], status_code=status.HTTP_200_OK)
async def get_reviews_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Получение всех активных отзывов конкретного товара по id
    :param product_id:
    :param db:
    :return:
    """
    stmt = await db.scalars(
        select(ProductModel).where(
            ProductModel.id == product_id,
            ProductModel.is_active == True
        )
    )

    product = stmt.first()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    result = await db.scalars(
        select(ReviewModel).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True
        )
    )

    review = result.all()

    return review
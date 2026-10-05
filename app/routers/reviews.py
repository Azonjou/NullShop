from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from starlette.status import HTTP_400_BAD_REQUEST

from app.auth import get_current_seller, get_current_buyer

from app.models.products import Product as ProductModel
from app.schemas import Product as ProductShema, ProductCreate

from app.models.reviews import Review as ReviewModel
from app.schemas import Review as ReviewShema, ReviewCreate

from app.models.categories import Category as CategoryModel
from app.db_depends import get_async_db

from app.models.users import User as UserModel
from app.auth import get_current_seller

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)

async def count_grade(product_id: int, db: AsyncSession):
    """
    Считает среднее арифметческое все оценок товара
    :param product_id:
    :param db:
    :return:
    """
    reviews_result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True
        )
    )

    avg_result = reviews_result.scalar() or 0.0
    if avg_result > 5.0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Grade too high")
    product = await db.get(ProductModel, product_id)
    product.rating = avg_result
    await db.commit()


@router.get("/", response_model=list[ReviewShema])
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    Получает список всех активнх отзывов
    :param db:
    :return:
    """
    result = await db.scalars(
        select(ReviewModel)
        .join(ProductModel)
        .where(
            ReviewModel.is_active == True,
            ProductModel.is_active == True,
        )
    )

    reviews = result.all()

    return reviews

@router.post("/", response_model=ReviewShema, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewCreate, current_user: UserModel = Depends(get_current_buyer), db: AsyncSession = Depends(get_async_db)):
    """
    Создание нового отзыва
    :param review:
    :param current_user:
    :param db:
    :return:
    """
    product_result = await db.scalars(
        select(ProductModel).where(
            ProductModel.id == review.product_id,
            ProductModel.is_active == True,
        )
    )

    product = product_result.first()

    if product is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product not found")

    if current_user.role != "buyer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to perform this action")

    count_reviews = await db.scalar(
        select(func.count(ReviewModel.id)).where(
            ReviewModel.is_active == True,
            ReviewModel.user_id == current_user.id,
        )
    )

    if count_reviews > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Review already exists")

    db_review = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    await count_grade(product.id, db)
    return db_review

@router.delete("/{review_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_review_id(review_id: int, current_user: UserModel = Depends(get_current_buyer), db: AsyncSession = Depends(get_async_db)):
    """
    Удаление отзыва (логическое удаление is_active=False)
    :param review_id:
    :param current_user:
    :param db:
    :return:
    """
    review_result = await db.scalars(
        select(ReviewModel).where(
            ReviewModel.id == review_id,
            ReviewModel.is_active == True,
        )
    )

    review = review_result.first()

    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found or not active")

    if current_user.role not in ("buyer", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to perform this action")

    product_result = await db.scalars(
        select(ProductModel).where(
            ProductModel.id == review.product_id,
        )
    )

    product = product_result.first()

    review.is_active = False
    await db.commit()
    await db.refresh(review)
    await count_grade(product.id, db)
    return {"message": "Review deleted"}
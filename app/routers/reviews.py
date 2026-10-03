from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
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

@router.get("/", response_model=list[ReviewShema])
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)):
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
    pass
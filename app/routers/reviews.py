from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST

from app.auth import get_current_seller
from app.models.products import Product as ProductModel
from app.schemas import Product as ProductShema, ProductCreate
from app.models.categories import Category as CategoryModel
from app.db_depends import get_async_db

from app.models.users import User as UserModel
from app.auth import get_current_seller


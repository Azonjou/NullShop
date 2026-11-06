from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi.security import OAuth2PasswordRequestForm

from app.models.users import User as UserModel
from app.db_depends import get_async_db
from app.auth import hash_password, verify_password, create_access_token, create_refresh_token, get_current_user

import jwt

from app.config import SECRET_KEY, ALGORITHM
from app.schemas import UserCreate, User as UserSchema, RefreshTokenRequest, ChangePasswordRequest

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Регистрирует нового пользователя с ролью 'buyer' or 'seller'
    """
    # Проверка уникальности id
    result = await db.scalars(
        select(UserModel).where(
            UserModel.email == user.email
        )
    )
    if result.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # Создание объекта пользователя с хешированным паролем
    db_user = UserModel(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role
    )

    # Добавление в сессию и сохранение в базе
    db.add(db_user)
    await db.commit()
    return db_user

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_async_db)):
    """
    Аутентифицирует пользователя и возвращает JWT с email, role и id.
    """
    result = await db.scalars(
        select(UserModel).where(UserModel.email == form_data.username, UserModel.is_active == True))
    user = result.first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role, "id": user.id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/access-token", response_model=dict)
async def access_token(body: RefreshTokenRequest, db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет access token, принимая refresh token
    """
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    refresh_token_now = body.refresh_token

    try:
        payload = jwt.decode(refresh_token_now, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")

        if email is None or token_type != "refresh":
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    result = await db.scalars(
        select(UserModel).where(
            UserModel.email == email,
            UserModel.is_active == True
        )
    )

    user = result.first()
    if user is None:
        raise credentials_exception

    new_access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )

    return {
        "access_token": new_access_token,
        token_type: "bearer",
    }

@router.post("/refresh-token")
async def refresh_token(body: RefreshTokenRequest, db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет refresh token, принимая старый refresh token в теле запроса
    """
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


    old_refresh_token = body.refresh_token

    try:
        payload = jwt.decode(old_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")

        #Проверяем что токен действительно refresh
        if email is None or token_type != "refresh":
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        #refresh token истек
        raise credentials_exception
    except jwt.PyJWTError:
        # подпись неверна или токен поврежден
        raise credentials_exception

    # Проверяем, что пользователь существует и активен
    result = await db.scalars(
        select(UserModel).where(
            UserModel.email == email,
            UserModel.is_active == True
        )
    )

    user = result.first()
    if user is None:
        raise credentials_exception

    # Генерируем новый refresh token
    new_refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )

    return {
        "refresh_token": new_refresh_token,
        token_type: "bearer",
    }

@router.put("/change-password", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def change_password(
        passwords: ChangePasswordRequest,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_user)
):
    old_pass, new_pass = passwords.old_password, passwords.new_password

    check_user = await db.scalar(
        select(UserModel).where(
            UserModel.email == current_user.email,
            UserModel.is_active == True
        )
    )

    if not check_user or not verify_password(old_pass, check_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    current_user.hashed_password = hash_password(passwords.new_password)

    await db.commit()
    return current_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def close_session_user(
        user_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect role",
        )

    check_user = await db.scalar(
        select(UserModel).where(
            UserModel.id == user_id,
            UserModel.is_active == True
        )
    )

    if not check_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or inactive")

    await db.execute(
        update(UserModel).where(
            UserModel.id == user_id,
        ).values(is_active=False)
    )
    await db.commit()
    await db.refresh(check_user)


from datetime import timedelta

from auth.jwttoken import create_access_token
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from src.models.sellers import Seller
from src.schemas import Token, AuthUser
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations import get_async_session, settings as auth

token_router = APIRouter(tags=["token"], prefix="/token")

@token_router.post(
    "/",
    response_model=Token,
    status_code=status.HTTP_200_OK,
)
async def login(
    user: AuthUser,
    session: AsyncSession = Depends(get_async_session),
):
    user_query = select(Seller).where(Seller.e_mail == user.e_mail)
    seller: Seller = await session.scalar(user_query)
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Пользователь не найден"
        )
    if seller.password != user.password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неверный пароль"
            )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.e_mail}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
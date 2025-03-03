from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select, func, cast
from src.models.sellers import Seller
from src.models.books import Book
from sqlalchemy.dialects.postgresql import JSONB
from src.schemas import IncomingSeller, ReturnedAllSellers, ReturnedSeller
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations import get_async_session
from sqlalchemy.orm import joinedload

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

# CRUD - Create, Read, Update, Delete

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания продавца в БД. Возвращает созданного продавца.
# @sellers_router.post("/sellers/", status_code=status.HTTP_201_CREATED)
@sellers_router.post(
    "/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED
)  # Прописываем модель ответа
async def create_seller(
    seller: IncomingSeller,
    session: DBSession,
):  
    new_seller = Seller(
        **{
            "first_name": seller.first_name,
            "last_name": seller.last_name,
            "e_mail": seller.e_mail,
            "password": seller.password,
        }
    )

    session.add(new_seller)
    await session.flush()

    return new_seller


# Ручка, возвращающая все продавцов
@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    # Хотим видеть формат
    # sellers: [{"id": 1, "first_name": "John", "last_name": "Doe", "e_mail": "john.doe@example.com"}, {...}]
    query = select(Seller)  # SELECT * FROM seller
    result = await session.execute(query)
    sellers = result.scalars().all()
    return {"sellers": sellers}


# Ручка для получение продавца по его ИД
@sellers_router.get("/{seller_id}", response_model=ReturnedSeller)
async def get_seller(seller_id: int, session: DBSession):
    result = await session.execute(
        select(
            Seller.id,
            Seller.first_name,
            Seller.last_name,
            Seller.e_mail,
            func.coalesce(
                func.jsonb_agg(
                    func.jsonb_build_object(
                        "id", Book.id,
                        "title", Book.title,
                        "author", Book.author,
                        "year", Book.year,
                        "pages", Book.pages
                    )
                ).filter(Book.id.isnot(None)),  # Исключаем NULL
                cast("[]", JSONB)  # Явное указание, что это JSONB
            ).label("books")
        )
        .outerjoin(Book, Book.seller_id == Seller.id)
        .filter(Seller.id == seller_id)
        .group_by(Seller.id)
    )
    
    seller = result.first()
    
    if not seller:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    seller_dict = seller._asdict()
    seller_dict["books"] = seller_dict["books"] if isinstance(seller_dict["books"], list) else []

    return seller_dict  # Преобразуем результат в словарь


# Ручка для удаления продавца
@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    ic(deleted_seller)  # Красивая и информативная замена для print. Полезна при отладке.
    if deleted_seller:
        await session.delete(deleted_seller)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для обновления данных о продавце
@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, new_seller_data: ReturnedSeller, session: DBSession):
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его. Заменяет то, что закомментировано выше.
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_seller_data.first_name
        updated_seller.last_name = new_seller_data.last_name
        updated_seller.e_mail = new_seller_data.e_mail

        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)

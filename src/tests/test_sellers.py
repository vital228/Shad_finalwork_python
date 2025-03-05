import pytest
from sqlalchemy import select
from src.models.books import Book
from src.models.sellers import Seller
from fastapi import status
from icecream import ic
from .support_func import create_seller, create_authorized_seller

# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "e_mail": "email@gmail.com",
        "password": "123456Fa",
    }
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    resp_seller_id = result_data.pop("id", None)
    assert resp_seller_id, "Seller id not returned from endpoint"

    assert result_data == {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "e_mail": "email@gmail.com",
    }


@pytest.mark.asyncio
async def test_create_seller_with_incorrect_email(async_client):
    data = {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "e_mail": "emailgmail.com",
        "password": "123456Fa",
    }
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_create_seller_with_existing_email(async_client, db_session):
    seller = await create_seller(db_session)
    data = {
        "first_name": "Ivans",
        "last_name": "Ivanova",
        "e_mail": "email@gmail.com",
        "password": "123456Fb",
    }
    response = await async_client.post("/api/v1/sellers/", json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {"detail": "Пользователь с таким e-mail уже существует"}

@pytest.mark.asyncio
async def test_create_seller_with_incorrect_password(async_client):
    data = {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "e_mail": "email@gmail.com",
        "password": "123456aa",
    }
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    seller = Seller(first_name="Ivan", last_name="Ivanov", e_mail="email@gmail.com", password="123456Fa")
    seller_2 = Seller(first_name="Peter", last_name="Petrov", e_mail="email_1@gmail.com", password="123456Fb")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert (
        len(response.json()["sellers"]) == 2
    )  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "id": seller.id,
                "e_mail": "email@gmail.com",
            },
            {
                "first_name": "Peter",
                "last_name": "Petrov",
                "id": seller_2.id,
                "e_mail": "email_1@gmail.com",
            },
        ]
    }


# Тест на ручку получения одной продавца
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    seller, access_token = await create_authorized_seller(db_session)
    seller_2 = await create_seller(db_session, email="email_1@gmail.com")

    response = await async_client.get(f"/api/v1/sellers/{seller.id}", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "id": seller.id,
        "e_mail": "email@gmail.com",
        "books": [],
    }

    response = await async_client.get(f"/api/v1/sellers/{seller_2.id}", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_403_FORBIDDEN


# Тест на ручку получения одной продавца c книгами
@pytest.mark.asyncio
async def test_get_single_seller_with_book(db_session, async_client):
    seller, access_token = await create_authorized_seller(db_session)

    book = Book(author="Lermontov", title="Mtziri", pages=510, year=2024, seller_id=seller.id)
    book_2 = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)
    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert len(response.json()["books"]) == 2
    assert response.json()["books"][0] == {
        "id": book.id,
        "title": "Mtziri",
        "author": "Lermontov",
        "year": 2024,
        "pages": 510,
    }
    


# Тест на ручку обновления продавца
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):

    seller = await create_seller(db_session)

    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json={
            "id": seller.id,
            "first_name": "Peter",
            "last_name": "Petrov",
            "e_mail": "email_1@gmail.com",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(Seller, seller.id)
    assert res.first_name == "Peter"
    assert res.last_name == "Petrov"
    assert res.e_mail == "email_1@gmail.com"




@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = await create_seller(db_session)

    ic(seller.id)

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()
    all_sellers = await db_session.execute(select(Seller))
    res = all_sellers.scalars().all()

    assert len(res) == 0


@pytest.mark.asyncio
async def test_delete_seller_with_invalid_seller_id(db_session, async_client):
    seller = Seller(first_name="Ivan", last_name="Ivanov", e_mail="email@gmail.com", password="123456Fa")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND

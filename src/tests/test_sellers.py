import pytest
from sqlalchemy import select
from src.models.sellers import Seller
from fastapi import status
from icecream import ic

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
        # "books": [],
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
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
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
                # "books": [],
            },
            {
                "first_name": "Peter",
                "last_name": "Petrov",
                "id": seller_2.id,
                "e_mail": "email_1@gmail.com",
                # "books": [],
            },
        ]
    }


# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = Seller(first_name="Ivan", last_name="Ivanov", e_mail="email@gmail.com", password="123456Fa")
    seller_2 = Seller(first_name="Peter", last_name="Petrov", e_mail="email_1@gmail.com", password="123456Fb")
    
    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "id": seller.id,
        "e_mail": "email@gmail.com",
        # "books": [],
    }


# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = Seller(first_name="Ivan", last_name="Ivanov", e_mail="email@gmail.com", password="123456Fa")

    db_session.add(seller)
    await db_session.flush()

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
    # assert res.books == []




@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = Seller(first_name="Ivan", last_name="Ivanov", e_mail="email@gmail.com", password="123456Fa")

    db_session.add(seller)
    await db_session.flush()
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

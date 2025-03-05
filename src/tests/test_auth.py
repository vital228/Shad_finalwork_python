import pytest
from fastapi import status
from .support_func import create_seller

# Тест на авторизацию пользователя
@pytest.mark.asyncio
async def test_login(async_client, db_session):
    seller = await create_seller(db_session)

    data = {
        "e_mail": "email@gmail.com",
        "password": "123456Fa",
    }
    response = await async_client.post("/api/v1/token/", json=data)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_login_incorrect_email(async_client, db_session):
    seller = await create_seller(db_session)

    data = {
        "e_mail": "emai@gmail.com",
        "password": "123456Fa",
    }
    response = await async_client.post("/api/v1/token/", json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {"detail": "Пользователь не найден"}

@pytest.mark.asyncio
async def test_login_incorrect_password(async_client, db_session):
    seller = await create_seller(db_session)

    data = {
        "e_mail": "email@gmail.com",
        "password": "123456Fb",
    }
    response = await async_client.post("/api/v1/token/", json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {"detail": "Неверный пароль"}
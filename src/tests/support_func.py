from src.models.sellers import Seller
from datetime import timedelta
from src.configurations import settings
from auth.jwttoken import create_access_token

# Вспомогательная функция для создания продавца
async def create_seller(db_session, email="email@gmail.com"):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail=email,
        password="123456Fa"
    )
    db_session.add(seller)
    await db_session.flush()
    return seller


# Вспомогательная функция для создания авторизованного продавца
async def create_authorized_seller(db_session, email="email@gmail.com"):
    seller = await create_seller(db_session, email)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": seller.e_mail}, expires_delta=access_token_expires
    )
    return seller, access_token

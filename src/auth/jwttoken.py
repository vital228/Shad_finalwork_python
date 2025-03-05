from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from schemas.auth import TokenData
from configurations import settings as auth


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, auth.SECRET_KEY, algorithm=auth.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentails_exception) -> str:
    try:
        playload = jwt.decode(
            token.credentials, auth.SECRET_KEY, algorithms=[auth.ALGORITHM]
        )
        login: str = playload.get("sub")
        if login is None:
            raise credentails_exception
        token_data = TokenData(login=login)

    except JWTError:
        raise credentails_exception from JWTError
    return token_data.login
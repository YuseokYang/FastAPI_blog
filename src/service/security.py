from datetime import datetime, timedelta, timezone
from typing import Annotated

from dotenv import load_dotenv
import os

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.orm import User
from database.repository import UserRepository

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/sign-in", auto_error=False)

async def get_current_user(
        user_repo: UserRepository = Depends(),
        token: str = Depends(oauth2_scheme),

) -> User:

    credentials_exception = HTTPException(status_code=401, detail="Not Authorized")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_repo.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user





def create_JWT(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": username,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)



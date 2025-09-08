from datetime import timedelta

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from splitwise.schemas.user import Token, UserOut, UserCreate, UserDTO
from .user import select_user_by_email
from splitwise.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from splitwise.models.user import User
from splitwise.logger import logger
from splitwise.config import settings


async def validate_user(
    user: UserDTO,
    session: AsyncSession,
) -> UserOut:
    cur_user: UserDTO = await select_user_by_email(user.email, session)
    if cur_user is None:
        logger.error(f"user - {user.email} is not registered")
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )
    if not verify_password(user.password, cur_user.password):
        logger.error(f"incorrect password for user - {cur_user.email}")
        raise HTTPException(
            status_code=401,
            detail="incorrect password",
        )
    return cur_user


async def register_new_user(user: UserCreate, session: AsyncSession):
    hashed_pwd = get_password_hash(user.password)

    cur_user = await select_user_by_email(user.email, session)
    if cur_user:
        logger.error(f"email {cur_user.email} already registered")
        raise HTTPException(
            status_code=400, detail=f"email - {cur_user.email} already registered"
        )
    try:
        new_user = User(email=user.email, password=hashed_pwd)
        session.add(new_user)
        await session.commit()
        return new_user
    except Exception as e:
        logger.error(f"exception - {e}")


async def reliase_token(cur_user: UserOut) -> str:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": cur_user.email}, expires_delta=access_token_expires
    )
    return access_token

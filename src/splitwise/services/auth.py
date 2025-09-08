from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from splitwise.schemas.user import Token, UserOut, UserCreate
from .user import select_user_by_email
from splitwise.utils.security import get_password_hash
from splitwise.models.user import User
from splitwise.logger import logger


async def login_for_access_token(email: EmailStr, password: str) -> Token:
    user: UserOut = validate_user(email, password)


async def validate_user(email: EmailStr, password: str) -> UserOut:
    user: UserOut = await select_user_by_email(email)


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

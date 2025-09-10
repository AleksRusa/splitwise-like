from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException, Request, Response

from splitwise.schemas.user import UserCreate, UserDTO, UserId, UserOut, Token
from splitwise.services.auth import (
    get_user_from_cookies,
    register_new_user,
    validate_user,
    reliase_token,
)
from splitwise.config import settings
from splitwise.database import get_db
from splitwise.logger import logger


router = APIRouter(prefix="/user", tags=["auth"])


@router.post("/register", response_model=UserOut)
async def user_register(new_user: UserCreate, session=Depends(get_db)) -> str:
    result = await register_new_user(new_user, session)
    logger.info(f"user {result.email} successfully created")
    return result


@router.post("/token")
async def login_for_access_token(
    response: Response, user: UserCreate, session=Depends(get_db)
) -> Token:
    try:
        cur_user = await validate_user(user, session)
        access_token = await reliase_token(cur_user)
        logger.info(f"user - {user.email} successfully logined")

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        return Token(access_token=access_token, token_type="bearer")
    except HTTPException:
        raise  # Пробрасываем HTTP-исключения как есть
    except Exception as e:
        logger.error(
            f"ошибка во время входа в аккаунт пользователя '{user.email}' - {e}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal authentication error",
        )


@router.get("/me")
async def get_current_user_from_token(
    request: Request, session=Depends(get_db)
) -> UserId:
    current_user = await get_user_from_cookies(request, session)
    return current_user

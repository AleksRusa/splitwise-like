from fastapi import Depends, APIRouter

from splitwise.schemas.user import UserCreate, UserOut
from splitwise.services.auth import register_new_user
from splitwise.database import get_db
from splitwise.logger import logger


router = APIRouter(prefix="/user", tags=["auth"])
"""
поступает POST запрос
валидируем входящие данные через pydantic schemas
получаем hash password
отправляем запрос в базу данных
обрабатываем ошибки
возвращаем ответ
"""


@router.post("/register", response_model=UserOut)
async def user_register(new_user: UserCreate, session=Depends(get_db)) -> str:
    result = await register_new_user(new_user, session)
    logger.info("user successfully created")
    return result

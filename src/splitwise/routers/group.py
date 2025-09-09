from fastapi import APIRouter, Depends
from splitwise.logger import logger
from splitwise.database import get_db
from splitwise.routers.auth import get_current_user_from_token
from splitwise.schemas.group import GroupCreate
from splitwise.schemas.user import UserId
from splitwise.services.group import create_group


router = APIRouter(prefix="/groups", tags=["groups"])

"""
создание группы, генерация токена для вступления
генерация ссылки для вступления
проверка тока для вступления и добавление пользователя
"""


@router.post("/create_new")
async def create_new_group(
    data: GroupCreate,
    session=Depends(get_db),
    user_id: UserId = Depends(get_current_user_from_token),
) -> str:
    new_group_name = await create_group(data, session, user_id.id)
    logger.info(f"group '{new_group_name}' successfully created")
    return f"group '{new_group_name}' successfully created"


@router.get("/join_link")
async def create_join_link(
    session=Depends(get_db),
    user_id: UserId = Depends(get_current_user_from_token),
) -> str:
    pass

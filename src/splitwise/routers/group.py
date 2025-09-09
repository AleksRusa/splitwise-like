from fastapi import APIRouter, Depends, Query
from splitwise.logger import logger
from splitwise.database import get_db
from splitwise.routers.auth import get_current_user_from_token
from splitwise.schemas.group import GroupCreate
from splitwise.schemas.user import UserId
from splitwise.services.group import (
    add_user_to_group_via_link,
    create_group,
    create_invite_link,
)


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
    group_id: int,
    session=Depends(get_db),
    user_id: UserId = Depends(get_current_user_from_token),
) -> dict:
    invite_link = await create_invite_link(group_id, session, user_id.id)
    return {"invite_link": invite_link}


@router.get("/join_group")
async def join_group_via_link(
    token: str = Query(..., description="Invite token from URL"),
    session=Depends(get_db),
    user_id: UserId = Depends(get_current_user_from_token),
) -> str:
    message = await add_user_to_group_via_link(token, session, user_id.id)
    return message

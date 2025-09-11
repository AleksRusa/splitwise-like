from fastapi import APIRouter, Depends, Query
from splitwise.logger import logger
from splitwise.database import get_db
from splitwise.routers.auth import get_current_user_from_token
from splitwise.schemas.group import GroupChangeData, GroupCreate
from splitwise.schemas.user import UserId
from splitwise.services.group import (
    add_user_to_group_via_link,
    change_group_data_by_id,
    create_group,
    create_invite_link,
    delete_group_by_id,
    get_group_by_group_id,
)
from splitwise.utils.decorators import validate_user_permissions_for_group_id


router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/create_new")
async def create_new_group(
    data: GroupCreate,
    session=Depends(get_db),
    user_id: int = Depends(get_current_user_from_token),
) -> str:
    new_group = await create_group(data, session, user_id)
    logger.info(f"group '{new_group.name}' successfully created - id={new_group.id}")
    return f"group '{new_group.name}' successfully created - id={new_group.id}"


@router.get("/join_link")
async def create_join_link(
    group_id: int,
    session=Depends(get_db),
    user_id: int = Depends(get_current_user_from_token),
) -> dict:
    invite_link = await create_invite_link(group_id, session, user_id)
    return {"invite_link": invite_link}


@router.get("/join_group")
async def join_group_via_link(
    token: str = Query(..., description="Invite token from URL"),
    session=Depends(get_db),
    user_id: int = Depends(get_current_user_from_token),
) -> str:
    message = await add_user_to_group_via_link(token, session, user_id)
    return message


@router.delete("/delete_group")
@validate_user_permissions_for_group_id()
async def delete_group(
    group_id: int,
    session=Depends(get_db),
    user_id: int = Depends(get_current_user_from_token),
) -> str:
    name = await delete_group_by_id(group_id, session, user_id)
    return f"group '{name}' deleted"


@router.patch("/change_group_data")
@validate_user_permissions_for_group_id()
async def chenge_group_data(
    group_id: int,
    data: GroupChangeData,
    session=Depends(get_db),
    user_id: int = Depends(get_current_user_from_token),
) -> str:
    message = await change_group_data_by_id(group_id, data, session, user_id)
    return message


@router.get("/get_group")
async def get_group(
    id: int,
    session=Depends(get_db),
    user_id: int = Depends(get_current_user_from_token),
) -> GroupChangeData:
    group = await get_group_by_group_id(id, session)
    return group

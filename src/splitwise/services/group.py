import secrets
from typing import Optional
from fastapi import HTTPException
from splitwise.config import settings
from splitwise.logger import logger
from splitwise.models.user import GroupMembers
from splitwise.schemas.user import UserId
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from splitwise.models.group import Group
from splitwise.schemas.group import GroupCreate


async def create_group(data: GroupCreate, session: AsyncSession, user_id: int) -> str:
    try:
        new_group = Group(
            name=data.name,
            description=data.description,
            group_owner_id=user_id,
            join_token=secrets.token_urlsafe(16),
        )
        session.add(new_group)
        await session.commit()
        await add_user_to_group(new_group.id, new_group.group_owner_id, session)
        return new_group.name
    except Exception as e:
        logger.error(f"exception - {e}")
        raise e


async def get_group_by_group_id(
    group_id: int, session: AsyncSession
) -> Optional[Group]:
    stmt = select(Group).where(Group.id == group_id)
    result = await session.execute(stmt)
    group = result.scalar_one_or_none()
    if not group:
        logger.error(f"group with id - '{group_id} is not found")
        raise HTTPException(status_code=403, detail=f"group not found")
    return group


async def get_group_by_join_token(token: str, session: AsyncSession) -> Optional[Group]:
    stmt = select(Group).where(Group.join_token == token)
    result = await session.execute(stmt)
    group = result.scalar_one_or_none()
    if not group:
        logger.error(f"group with invite token - '{token}' is not found")
        raise HTTPException(status_code=403, detail=f"group not found")
    return group


async def create_invite_link(group_id: int, session: AsyncSession, user_id: int):
    group: Group = await get_group_by_group_id(group_id=group_id, session=session)
    if group.group_owner_id != user_id:
        logger.error(
            f"user - '{user_id}' don't have enough permissions in group - '{group_id}'"
        )
        raise HTTPException(status_code=403, detail="Not enough permissions")
    url = f"{settings.BASE_APP_URL}/groups/join_group?token={group.join_token}"
    return url


async def get_group_members(group_id: int, session: AsyncSession):
    stmt = select(GroupMembers.user_id).where(GroupMembers.group_id == group_id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def add_user_to_group(group_id: int, user_id: int, session: AsyncSession):
    try:
        group_member = GroupMembers(user_id=user_id, group_id=group_id)
        session.add(group_member)
        await session.commit()
        logger.info(
            f"user with id: '{user_id}' successfully added to group - '{group_id}'"
        )
        return "successfully added"
    except Exception as e:
        logger.error(f"exception - {e}")
        raise e


async def add_user_to_group_via_link(
    token: str, session: AsyncSession, user_id: int
) -> str:
    group = await get_group_by_join_token(token, session)
    group_members = await get_group_members(group.id, session)
    if user_id in group_members:
        raise HTTPException(status_code=409, detail="user already in a group")
    result = await add_user_to_group(group.id, user_id, session)
    return result

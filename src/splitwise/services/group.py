import secrets
from typing import Optional
from fastapi import HTTPException
from splitwise.config import settings
from splitwise.logger import logger
from splitwise.models.user import GroupMembers
from splitwise.schemas.user import UserId
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from splitwise.models.group import Group
from splitwise.schemas.group import GroupChangeData, GroupCreate


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


async def get_group_owner_by_group_name(group_name: str, session: AsyncSession) -> int:
    stmt = select(Group.group_owner_id).where(Group.name == group_name)
    result = await session.execute(stmt)
    group_owner = result.scalar_one_or_none()
    if not group_owner:
        logger.error(f"group '{group_name}' is not found")
        raise HTTPException(status_code=403, detail=f"group not found")
    return group_owner


async def get_group_by_name(group_name: str, session: AsyncSession) -> Group:
    stmt = select(Group).where(Group.name == group_name)
    result = await session.execute(stmt)
    group = result.scalar_one_or_none()
    if not group:
        logger.error(f"group '{group_name}' is not found")
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
    await validate_permissions_for_group(user_id, group.group_owner_id)
    url = f"{settings.BASE_APP_URL}/groups/join_group?token={group.join_token}"
    return url


async def get_group_members(group_id: int, session: AsyncSession):
    stmt = select(GroupMembers.user_id).where(GroupMembers.group_id == group_id)
    result = await session.execute(stmt)
    members = result.scalars().all()
    return members


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


async def validate_permissions_for_group(user_id: int, group_owner: int):
    if group_owner != user_id:
        logger.error(f"user - '{user_id}' don't have enough permissions in group")
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return None


async def delete_group_by_id(
    group_id: int,
    session: AsyncSession,
    user_id: int,
) -> str:
    try:
        stmt = delete(Group).where(Group.id == group_id).returning(Group.name)
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar()
    except Exception as e:
        logger.error(f"exception - {e}, while deleting group")
        raise e


async def change_group_data_by_id(
    group_id: int,
    data: GroupChangeData,
    session: AsyncSession,
    user_id: int,
) -> str:
    try:
        update_values = data.model_dump(exclude_unset=True)
        stmt = update(Group).where(Group.id == group_id).values(**update_values)
        await session.execute(stmt)
        await session.commit()
        logger.info(
            f"fields {update_values} successfully updated in group - '{group_id}"
        )
        return "fields successfully updated"
    except Exception as e:
        logger.error(f"exception - {e}, while updating group")
        raise e

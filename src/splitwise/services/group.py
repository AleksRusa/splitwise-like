import secrets
from splitwise.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession

from splitwise.models.group import Group
from splitwise.schemas.group import GroupCreate


async def create_group(data: GroupCreate, session: AsyncSession, user_id: int) -> str:
    try:
        new_group = Group(
            name=data.name,
            description=data.description,
            group_owner=user_id,
            join_token=secrets.token_urlsafe(16),
        )
        session.add(new_group)
        await session.commit()
        return new_group.name
    except Exception as e:
        logger.error(f"exception - {e}")
        raise e

from functools import wraps
from typing import Callable
from fastapi import HTTPException
from splitwise.models.group import Group
from splitwise.logger import logger
from splitwise.schemas.group import GroupOwner
from splitwise.services.group import (
    get_group_by_group_id,
    get_group_by_name,
    get_group_members,
)


def validate_user_permissions_for_group_id():
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            *args,
            **kwargs,
        ):
            group_id = kwargs.get("group_id")
            user_id = kwargs.get("user_id")
            session = kwargs.get("session")
            group: Group = await get_group_by_group_id(group_id, session)
            if group.group_owner_id != user_id:
                logger.error(
                    f"user - '{user_id}' don't have enough permissions in group"
                )
                raise HTTPException(status_code=403, detail="Not enough permissions")
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def validate_user_membership_in_group():
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            *args,
            **kwargs,
        ):
            group_id = kwargs.get("group_id")
            user_id = kwargs.get("user_id")
            session = kwargs.get("session")
            group_members: list[int] = await get_group_members(group_id, session)
            if user_id not in group_members:
                logger.error(f"user_id={user_id} not in group_id]{group_id} members")
                raise HTTPException(
                    status_code=400,
                    detail="user not in group members",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# def validate_user_permissions_for_group_name():
#     def decorator(func: Callable) -> Callable:
#         @wraps(func)
#         async def wrapper(
#             group_name: str,
#             user_id: int,
#             session: AsyncSession,
#             *args,
#             **kwargs,
#         ):
#             group: Group = await get_group_by_name(group_name, session)
#             if group.group_owner_id != user_id:
#                 logger.error(
#                     f"user - '{user_id}' don't have enough permissions in group"
#                 )
#                 raise HTTPException(status_code=403, detail="Not enough permissions")
#             return await func(user_id, session, *args, **kwargs)

#         return wrapper

#     return decorator

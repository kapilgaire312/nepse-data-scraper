from typing import TYPE_CHECKING

from exceptions import AccessTokenInvalidError

if TYPE_CHECKING:
    from classes.nepse_session import NepseSession


def refetch_on_unauthorized(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except AccessTokenInvalidError:
            object_instance: NepseSession = args[0]

            # refreh the token
            await object_instance.refresh_session()

            return await func(*args, **kwargs)

    return wrapper

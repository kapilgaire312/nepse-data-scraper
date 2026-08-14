from exceptions import (
    AccessTokenFetchError,
    AccessTokenInvalidError,
    InvalidServerResponseError,
)
from fetch_handlers import get_access_and_refresh_token, get_market_open_info
from main import access_tokens, market_id
from modify_access_token import modify_access_token
from utils import calculate_client_id


class SessionInfo:
    def __init__(self) -> None:
        # token to be sent to client to verify identity
        self.access_token: str | None = None
        # token which refreshes access_token when it expires
        self.refresh_token: str | None = None

        # salt values sent by server in fetch_token_endpint,
        # are used to create a id which needs to be sent as payload to server when requesting data, stays same for one session.
        self.access_tokens: list[int] = []

        # id to be sent to server when requesting the data
        self.client_id: int | None = None

        # id returned byr market_open_endpoint,
        # used to calculate the client_id
        self.market_id: int | None = None

    async def set_access_and_refresh_token(self) -> None:
        try:
            data = await get_access_and_refresh_token()

            self.refresh_token = data.get("refreshToken")

            self.access_tokens = [
                data.get("salt1"),
                data.get("salt2"),
                data.get("salt3"),
                data.get("salt4"),
                data.get("salt5"),
            ]

            # update the access token sent by server with the wasm file
            original_access_token = data.get("accessToken")
            updated_access_token = modify_access_token(
                original_access_token=original_access_token,
                salt_values=self.access_tokens,
            )
            self.access_token = updated_access_token

        except AccessTokenFetchError as e:
            print("Failed setting the access token.")
            print("Error occured:", e.__cause__)

        except InvalidServerResponseError as e:
            print(e)

        except Exception as e:
            print(e)

    async def set_market_id(self):
        try:
            data = await get_market_open_info(self.access_token)
            self.market_id = data.get("id")

        except AccessTokenInvalidError as e:
            print(e)

        except InvalidServerResponseError as e:
            print(e)

        except Exception as e:
            print(e)

    def set_client_id(self):
        if (self.market_id is None) or (not self.access_tokens):
            print("Market id and/or access_tokens not set.")
            return
        self.client_id = calculate_client_id(
            market_id=self.market_id, access_tokens=self.access_tokens
        )

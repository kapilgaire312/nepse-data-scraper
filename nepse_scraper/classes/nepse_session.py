import asyncio
from datetime import date

from nepse_scraper.classes.token_response import TokenResponse
from nepse_scraper.decorators.refetch_on_unauthorized import refetch_on_unauthorized
from nepse_scraper.exceptions import AccessTokenInvalidError, MarketIdInvalidError
from nepse_scraper.fetch_handlers import (
    fetch_stock_data,
    get_access_and_refresh_token,
    get_market_open_info,
    refresh_access_token,
)
from nepse_scraper.utils import calculate_client_id, set_session_data


class NepseSession:
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

        # initialize the lock
        self._lock: asyncio.Lock = asyncio.Lock()

    async def set_access_and_refresh_token(self) -> None:
        """
        Fetches access token, refresh token and access tokens(salt values) and sets them.

        Raises:
            AccessTokenFetchError : If it fails to fetch the access token,refresh token and salt values
            InvalidServerResponseError : If the Nepse responded a non json data on 200 status.

        """

        data: TokenResponse = await get_access_and_refresh_token()
        set_session_data(self, data)

    @refetch_on_unauthorized
    async def set_market_id(self) -> None:
        """
        Fetches market-open info and sets self.market_id.

        Raises:
            AccessTokenInvalidError: If self.access_token is None/invalid/expired.
            InvalidServerResponseError: If the Nepse responded a non json data on 200 status.
            httpx.HTTPStatusError : If the Nepse responds with status code 4xx or 5xx.

        """

        data = await get_market_open_info(self.access_token)
        self.market_id = data.get("id")

    def set_client_id(self) -> None:
        """
        Calculates client id from market_id, access_token and access_tokens.

        Raises:
            AccessTokenInvalidError: If self.access_token is None/invalid/expired.
            MarketIdInvalidError: If the self.market_id is None.
        """

        if self.access_token is None:
            raise AccessTokenInvalidError()

        if self.market_id is None:
            raise MarketIdInvalidError()

        # get todays day int value
        day = date.today().day

        self.client_id = calculate_client_id(
            market_id=self.market_id, access_tokens=self.access_tokens, day=day
        )

    @refetch_on_unauthorized
    async def get_stocks_data(self, size, offset, market_date) -> list[dict]:
        """
        Fetches the list of stock data.

        Args:
            size: Number of stocks to fetch.
            offset:
            market_date: The date of which the stock data is to be fetched.

        Returns:
            List of dict containing info of the stocks.

        Raises:
            AccessTokenInvalidError: If self.access_token is None/invalid/expired.
            InvalidServerResponseError: If the Nepse responded a non json data on 200 status.
            httpx.HTTPStatusError : If the Nepse responds with status code 4xx or 5xx.

        """

        data = await fetch_stock_data(
            access_token=self.access_token,
            client_id=self.client_id,
            market_date=market_date,
            size=size,
            offset=offset,
        )

        return data

    async def refresh_session(self):
        """
        Calls the set_access_and_refresh_token() if access_token is none,
        or refeches the session data if access_token is expired/invalid.

        Raises:
            AccessTokenFetchError : If it fails to fetch the access token,refresh token and salt values
            InvalidServerResponseError : If the Nepse responded a non json data on 200 status.

            httpx.HTTPStatusError : If the Nepse responds with status code 4xx or 5xx.


        """

        async with self._lock:
            if self.access_token is None or self.refresh_token is None:
                await self.set_access_and_refresh_token()

            else:
                data: TokenResponse = await refresh_access_token(
                    access_token=self.access_token, refresh_token=self.refresh_token
                )

                set_session_data(self, data=data)

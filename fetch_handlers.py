from typing import TypedDict

import httpx

from exceptions import (
    AccessTokenFetchError,
    AccessTokenInvalidError,
    InvalidServerResponseError,
)
from utils import get_full_headers

default_headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36",
    "Referer": "https://www.nepalstock.com/today-price",
}


class TokenResponse(TypedDict):
    accessToken: str
    refreshToken: str
    salt1: int
    salt2: int
    salt3: int
    salt4: int
    salt5: int


async def get_access_and_refresh_token() -> TokenResponse:
    fetch_token_endpint = "https://www.nepalstock.com/api/authenticate/prove"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url=fetch_token_endpint, headers=default_headers)

            # raise error if status code in in 4xx or 5xx
            res.raise_for_status()

            try:
                data = res.json()
                print(data)
                return data

            except ValueError as e:
                print(res.text)
                raise InvalidServerResponseError("Invalid response from server.") from e

    except httpx.HTTPStatusError as http_err:
        print(f"Http error occured: {http_err}")
        raise AccessTokenFetchError() from http_err

    except InvalidServerResponseError:
        raise

    except Exception as e:
        print(e)
        raise AccessTokenFetchError() from e


async def get_market_open_info(access_token: str | None):
    market_open_endpoint = "https://www.nepalstock.com/api/nots/nepse-data/market-open"
    if access_token is None:
        raise AccessTokenInvalidError("Access token is not set!")

    try:
        # full headers
        full_headers = get_full_headers(
            default_headers=default_headers, access_token=access_token
        )

        # send request
        async with httpx.AsyncClient() as client:
            res = await client.get(url=market_open_endpoint, headers=full_headers)

            res.raise_for_status()

            try:
                data = res.json()
                return data

            except ValueError as e:
                print(res.text)
                raise InvalidServerResponseError("Invalid response from server.") from e

    except InvalidServerResponseError:
        raise

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        if status_code == 401:
            raise AccessTokenInvalidError() from e

        raise

    except Exception as e:
        print(e)

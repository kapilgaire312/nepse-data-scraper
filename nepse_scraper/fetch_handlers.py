import httpx

from nepse_scraper.classes.token_response import TokenResponse
from nepse_scraper.exceptions import (
    AccessTokenFetchError,
    AccessTokenInvalidError,
    InvalidServerResponseError,
)
from nepse_scraper.utils import get_full_headers

default_headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36",
    "Referer": "https://www.nepalstock.com/today-price",
}


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
        raise


async def fetch_stock_data(
    market_date,
    access_token,
    client_id,
    size=20,
    offset=0,
) -> list[dict]:
    fetch_endpoint = f"https://www.nepalstock.com/api/nots/nepse-data/today-price?page={offset}&size={size}&businessDate={market_date}"
    try:
        if access_token is None:
            raise AccessTokenInvalidError()

        # full header
        full_headers = get_full_headers(
            default_headers=default_headers, access_token=access_token
        )

        payload = {"id": client_id}

        async with httpx.AsyncClient() as client:
            res = await client.post(
                url=fetch_endpoint, headers=full_headers, json=payload
            )

            res.raise_for_status()

            try:
                return res.json()

            except ValueError as e:
                print(res.text)
                raise InvalidServerResponseError() from e

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        if status_code == 401:
            raise AccessTokenInvalidError() from e

        raise

    except InvalidServerResponseError:
        raise

    except AccessTokenInvalidError:
        raise

    except Exception as e:
        print("error coccures", e)
        raise


async def refresh_access_token(access_token: str, refresh_token: str):
    endpoint = "https://www.nepalstock.com/api/authenticate/refresh-token"

    try:
        async with httpx.AsyncClient() as client:
            full_headers = get_full_headers(
                default_headers=default_headers, access_token=access_token
            )

            payload = {"refreshToken": refresh_token}

            res = await client.post(url=endpoint, headers=full_headers, json=payload)

            res.raise_for_status()

            try:
                data = res.json()
                return data

            except ValueError:
                print(res.text)
                raise InvalidServerResponseError()

    except InvalidServerResponseError:
        raise

    except Exception:
        print("error occured")
        raise

import asyncio

import httpx

from exceptions import AccessTokenFetchError

default_headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36",
    "Referer": "https://www.nepalstock.com/today-price",
}


async def get_access_and_refresh_token() -> dict[str, str | bool | int]:
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

            except ValueError:
                print(res.text)
                raise Exception("Invalid response from server.")

    except httpx.HTTPStatusError as http_err:
        print(f"Http error occured: {http_err}")
        raise AccessTokenFetchError() from http_err

    except Exception as e:
        print(e)
        raise AccessTokenFetchError() from e


asyncio.run(get_access_and_refresh_token())

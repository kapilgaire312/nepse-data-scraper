import requests
from requests import HTTPError, Response

from exceptions import AccessTokenFetchError

page = 1
size = 20
market_date = "2026-08-05"
default_headers = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36",
}
endpoint = f"https://www.nepalstock.com/api/nots/nepse-data/today-price?page={page}&size={size}&businessDate={market_date}"
refresh_endpoint = ""
fetch_token_endpint = "https://www.nepalstock.com/api/authenticate/prove"


def get_access_and_refresh_token():
    try:
        res: Response = requests.get(
            url=fetch_token_endpint,
            headers=default_headers,
        )

        # raise error if status code in in 4xx or 5xx
        res.raise_for_status()

        data = res.json()

        return {
            "access_token": data.get("accessToken"),
            "refresh_token": data.get("refreshToken"),
        }

    except HTTPError as http_err:
        print(f"Http error occured: {http_err}")
        raise AccessTokenFetchError() from http_err

    except Exception as e:
        print(e)
        raise AccessTokenFetchError() from e


print(get_access_and_refresh_token())

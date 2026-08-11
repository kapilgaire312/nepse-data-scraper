from datetime import date
from time import sleep

import requests
from requests import HTTPError, Response

from dummy_data_arr import dummyData
from exceptions import AccessTokenFetchError
from utils import get_full_headers

page = 1
size = 20
market_date = "2026-08-05"
default_headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36",
    "Referer": "https://www.nepalstock.com/today-price",
}
refresh_endpoint = ""
fetch_token_endpint = "https://www.nepalstock.com/api/authenticate/prove"

# token to be sent to client to verify identity
access_token: str | None = None
# token which refreshes access_token when it expires
refresh_token: str | None = None

# salt values sent by server in fetch_token_endpint,
# are used to create a id which needs to be sent as payload to server when requesting data, stays same for one session.
access_tokens: list = []

# id to be sent to server when requesting the data
client_id: int | None = None

# id returned byr market_open_endpoint,
# used to calculate the client_id
market_id: int | None = None

today_date = date.today().strftime("%Y-%m-%d")


def set_access_and_refresh_token():
    global access_token
    global refresh_token

    try:
        res: Response = requests.get(
            url=fetch_token_endpint,
            headers=default_headers,
        )

        # raise error if status code in in 4xx or 5xx
        res.raise_for_status()

        data = res.json()

        # seed access_token adn refresh_token
        access_token = data.get("accessToken", None)
        refresh_token = data.get("refreshToken", None)
        print(data)

        # seed the salt values
        access_tokens.append(data.get("salt1"))
        access_tokens.append(data.get("salt2"))
        access_tokens.append(data.get("salt3"))
        access_tokens.append(data.get("salt4"))
        access_tokens.append(data.get("salt5"))

        sleep(2)
        get_market_open_info()

    except HTTPError as http_err:
        print(f"Http error occured: {http_err}")
        raise AccessTokenFetchError() from http_err

    except Exception as e:
        print(e)
        raise AccessTokenFetchError() from e


def fetch_stock_data(size=20, offset=0, market_date=today_date):
    endpoint = f"https://www.nepalstock.com/api/nots/nepse-data/today-price?page={offset}&size={size}&businessDate={market_date}"
    try:
        if access_token is None:
            tries = 3

            while access_token is None and tries > 0:
                set_access_and_refresh_token()
                if access_token is not None:
                    break
                tries -= 1

            else:
                raise Exception("Cannot set the accessToken")

        # full header
        full_header = get_full_headers(
            default_headers=default_headers, access_token=access_token
        )

        res = requests.post(endpoint, headers=full_header)

        print(res.status_code)
        # print(res.json())

    except Exception as e:
        print("error coccures", e)


def get_market_open_info():
    market_open_endpoint = "https://www.nepalstock.com/api/nots/nepse-data/market-open"
    if access_token is None:
        raise Exception("Access token is not set!")

    try:
        # full headers
        full_headers = get_full_headers(
            default_headers=default_headers, access_token=access_token
        )

        print(full_headers)

        # send request
        res = requests.get(market_open_endpoint, headers=full_headers)

        res.raise_for_status()
        print(res.status_code)
        print(res.text)

        url = "https://www.nepalstock.com/api/nots/nepse-data/market-open"

        token = "Salter eyJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiYWxnIjoiZGlyIn0..UXok7b1RiBvfmf1BZSCiWw.NAQZ-t35YdCoT4bRE6tA9GH1fCaJEAr8NxIfx1Sto4Hpg3My5CJcH0LmPEfdBujFrsceMQFaYKEwzh7NSYyLWjMc3xb8l7scjxkfqPGSWD2LB36LssrIPUl_YvfkiRCo7Uh_VgJ-7f6a22_nCiimlA.AJ6YK6TpW1iHC0A8M9YFZg"

        headers = {
            "Authorization": token,
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.nepalstock.com/today-price",
            "Origin": "https://www.nepalstock.com",
            "User-Agent": "Mozilla/5.0",
        }

        response = requests.get(url, headers=headers)

        print("Status:", response.status_code)
        print("Response:")

        try:
            print(response.json())
        except ValueError:
            print(response.text)

    except Exception as e:
        print(e)


def set_client_id():
    global client_id

    # get todays day int value
    day = date.today().day
    dummyId = market_id

    # calculating id based on nepalstock website
    l = dummyData[dummyId] + dummyId + 2 * day

    selector: int = 1 if (l % 10 < 5) else 3

    id = l + access_tokens[selector] * day - access_tokens[selector - 1]
    client_id = id


# get_market_open_info()
set_access_and_refresh_token()

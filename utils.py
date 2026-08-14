from datetime import date

from dummy_data_arr import dummyData


def get_full_headers(default_headers, access_token):
    # construct the authorization header
    auth_header = {
        "Authorization": f"Salter {access_token}",
    }

    # full header
    full_header = default_headers | auth_header
    return full_header


def calculate_client_id(market_id: int, access_tokens: list[int]) -> int:
    # get todays day int value
    day = date.today().day
    dummyId = market_id

    # calculating id based on nepalstock website
    l = dummyData[dummyId] + dummyId + 2 * day

    selector: int = 1 if (l % 10 < 5) else 3

    id = l + access_tokens[selector] * day - access_tokens[selector - 1]
    return id

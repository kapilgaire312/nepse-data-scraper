from classes.nepse_session import NepseSession
from classes.token_response import TokenResponse
from dummy_data_arr import dummyData
from modify_access_token import modify_access_token


def get_full_headers(default_headers, access_token):
    # construct the authorization header
    auth_header = {
        "Authorization": f"Salter {access_token}",
    }

    # full header
    full_header = default_headers | auth_header
    return full_header


def calculate_client_id(market_id: int, access_tokens: list[int], day) -> int:
    dummyId = market_id

    # calculating id based on nepalstock website
    l = dummyData[dummyId] + dummyId + 2 * day

    selector: int = 1 if (l % 10 < 5) else 3

    id = l + access_tokens[selector] * day - access_tokens[selector - 1]
    return id


def set_session_data(self: NepseSession, data: TokenResponse):
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

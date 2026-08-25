from typing import TypedDict


class TokenResponse(TypedDict):
    accessToken: str
    refreshToken: str
    salt1: int
    salt2: int
    salt3: int
    salt4: int
    salt5: int

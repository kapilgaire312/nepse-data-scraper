class AccessTokenFetchError(Exception):
    """Error occured when it fails to fetch the access token and refresh token."""

    pass


class AccessTokenInvalidError(Exception):
    """Error raised when the access token is None or invalid."""

    pass


class InvalidServerResponseError(Exception):
    """Error raised when server returns 200 but invalid response."""

    pass


class MarketIdInvalidError(Exception):
    """Error raised when the market_id is None."""

    pass

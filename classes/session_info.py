class SessionInfo:
    def __init__(self) -> None:
        # token to be sent to client to verify identity
        self.access_token: str | None = None
        # token which refreshes access_token when it expires
        self.refresh_token: str | None = None

        # salt values sent by server in fetch_token_endpint,
        # are used to create a id which needs to be sent as payload to server when requesting data, stays same for one session.
        self.access_tokens: list = []

        # id to be sent to server when requesting the data
        self.client_id: int | None = None

        # id returned byr market_open_endpoint,
        # used to calculate the client_id
        self.market_id: int | None = None

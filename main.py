import asyncio

from classes.nepse_session import NepseSession


# get_market_open_info()
async def main():
    nepse_session = NepseSession()
    await nepse_session.set_access_and_refresh_token()
    await nepse_session.set_market_id()
    nepse_session.set_client_id()
    data = await nepse_session.get_stocks_data(
        size=20, offset=0, market_date="2026-08-05"
    )
    print(data)


asyncio.run(main())

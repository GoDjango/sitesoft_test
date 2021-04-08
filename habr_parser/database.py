import asyncio
import asyncpg

import settings


class Database:
    def __init__(self):
        self.database = settings.db_name
        self.user = settings.db_user
        self.host = settings.db_host
        self.port = settings.db_port

    async def __aenter__(self):
        self.conn = await asyncpg.connect(host=self.host,
                                          user=self.user,
                                          port=self.port,
                                          database=self.database,
                                          )
        return self.conn

    async def __aexit__(self, *args, **kwargs):
        await self.conn.close()


# usage example
async def main():
    import datetime, pytz
    async with Database() as conn:
        result = await conn.fetch("""SELECT * FROM habr_hub""")
        for res in result:
            d = res['nextcall']
            d_with_tz = datetime.datetime(
                year=d.year,
                month=d.month,
                day=d.day,
                hour=d.hour,
                minute=d.minute,
                second=d.second,
                tzinfo=pytz.UTC,
                )

            print(d_with_tz, datetime.datetime.now(tz=pytz.UTC)+datetime.timedelta(minutes=10))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

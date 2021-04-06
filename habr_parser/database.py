import asyncio
import asyncpg


class Database:
    def __init__(self, database, user, host='localhost', port='5432'):
        self.database = database
        self.user = user
        self.host = host
        self.port = port

    async def __aenter__(self):
        self.conn = await asyncpg.connect(host=self.host,
                                          user=self.user,
                                          port=self.port,
                                          database=self.database,
                                          )
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.conn.close()

    async def execute(self, query):
        return await self.conn.fetchrow(query)


# async def main():
#     async with Database(database='habr_parser', user='andrey') as db:
#         result = await db.execute()

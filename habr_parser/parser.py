import asyncio
import aiohttp
import logging
import datetime

from bs4 import BeautifulSoup

from . import database
from . import settings

_logger = logging.getLogger(__name__)


class Base:
    def __init__(self, url, name):
        self.url = url
        self.name = name

    async def execute(self, query):
        async with database.Database(database=settings.db_name,
                                     user=settings.db_user,
                                     host=settings.db_host,
                                     port=settings.db_port,
                                     ) as db:
            result = await db.execute(query)
        return result


class Post(Base):
    def __init__(self, url, name):
        super().__init__(url=url, name=name)
        self.author = False
        self.hab = False
        self.publish_date = False


class Hab(Base):
    def __init__(self, url, name):
        super().__init__(url=url, name=name)
        self.period = 10
        self.nextcall = False

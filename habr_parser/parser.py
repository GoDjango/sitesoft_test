import asyncio
import aiohttp
import logging
import datetime
import dateutil.parser

from bs4 import BeautifulSoup

import database


_logger = logging.getLogger(__name__)


class Base:
    def __init__(self, url):
        self.url = url
        self.content = None

    async def get_content(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                result = await response.read()
        return result

    async def write(self, items):
        """
        Write data to database
        :param items: [(field, value), ...]
        :return:
        """
        raise NotImplementedError()

    async def run(self):
        raise NotImplementedError()


class Post(Base):
    def __init__(self, hub_id, **kwargs):
        super().__init__(**kwargs)
        self.hub_id = hub_id

    async def set_content(self):
        content = await self.get_content()
        self.content = BeautifulSoup(content, features='lxml')

    def get_post_info(self):
        return self.content.find('article')

    def get_author(self):
        post_info = self.get_post_info()
        return post_info.header.a.find('span', {'class': 'user-info__nickname'})

    @property
    def author(self):
        return self.get_author().string

    @property
    def author_url(self):
        return self.get_author()['href']

    @property
    def published_datetime(self):
        post_info = self.get_post_info()
        published_datetime = post_info.span['data-time_published']
        return dateutil.parser.parse(published_datetime)

    @property
    def publish_date_str(self):
        publish_datetime = self.published_datetime
        return publish_datetime.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def name(self):
        return self.get_post_info().h1.span.string

    async def run(self):
        create_post = False
        async with database.Database() as db:
            author_query = f"""SELECT id FROM habr_author WHERE name = '{self.author}'"""
            author = await db.fetchrow(author_query)
            if author is None:
                await db.execute(f"""INSERT INTO habr_author (name, url)
                                     VALUES ({self.author}, {self.author_url})
                                     """)
                # I can't get id, so repeat
                author = await db.fetchrow(author_query)
            author_id = author['id']

            post = await db.fetchrow(f"""SELECT id
                                         FROM habr_post
                                         WHERE name = {self.name}
                                               and author_id = {author_id}
                                               and url = {self.url}
                                         """)
            if post is None:
                await db.execute(
                    f"""INSERT
                        INTO habr_post (name, url, author_id, publish_date, hub_id)
                        VALUES
                        ('{self.name}', '{self.url}', {author_id}, '{self.publish_date_str}', {self.hub_id})
                        """
                )
                create_post = True
        return create_post


class Hub(Base):
    pass


class Parser:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def get_hubs(self):
        async with database.Database() as db:
            result = await db.fetch("""SELECT * FROM habr_hub""")
        return result

    async def get_posts(self):
        hubs = await self.get_hubs()
        for hub in hubs:
            pass

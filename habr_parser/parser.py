import datetime
import pytz
import dateutil.parser

import asyncio
import aiohttp
from aiologger import Logger
from aiologger.formatters.base import Formatter

from bs4 import BeautifulSoup

import database


queue = asyncio.Queue()
max_parallel = 4
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
_logger = Logger.with_default_handlers(name='parser',
                                       formatter=Formatter('%(asctime)-15s %(levelname)s %(name)s %(message)s'),
                                       )


class Base:
    def __init__(self, url):
        self.url = url
        self.content = None

    async def get_content(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                result = await response.read()
        await asyncio.sleep(1)
        return result

    async def set_content(self):
        content = await self.get_content()
        self.content = BeautifulSoup(content, features='lxml')

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

    def get_post_info(self):
        return self.content.find('article')

    def get_author_a_teg(self):
        post_info = self.get_post_info()
        return post_info.header.a

    @property
    def author(self):
        return self.get_author_a_teg().find('span', {'class': 'user-info__nickname'}).string

    @property
    def author_url(self):
        return self.get_author_a_teg()['href']

    @property
    def published_datetime(self):
        post_info = self.get_post_info()
        published_datetime = post_info.div.header.find('span', {'class': 'post__time'})['data-time_published']
        return dateutil.parser.parse(published_datetime)

    @property
    def publish_date_str(self):
        publish_datetime = self.published_datetime
        return publish_datetime.strftime(DATETIME_FORMAT)

    @property
    def name(self):
        return self.get_post_info().h1.span.string

    async def run(self):
        await self.set_content()

        async with database.Database() as db:
            author_query = f"""SELECT * FROM habr_author WHERE name = '{self.author}'"""
            author = await db.fetchrow(author_query)
            if author is None:
                await db.execute(f"""INSERT INTO habr_author (name, url)
                                     VALUES ('{self.author}', '{self.author_url}')
                                     """)
                # I can't get id, so repeat
                author = await db.fetchrow(author_query)
            author_id = author['id']

            post = await db.fetchrow(f"""SELECT id
                                         FROM habr_post
                                         WHERE name = '{self.name}'
                                               and author_id = {author_id}
                                               and url = '{self.url}'
                                         """)
            if post is None:
                await db.execute(
                    f"""INSERT
                        INTO habr_post (name, url, author_id, publish_date, hub_id)
                        VALUES
                        ('{self.name}', '{self.url}', {author_id}, '{self.publish_date_str}', {self.hub_id})
                        """
                )
                _logger.info(f'Post created: {self.name} ({author["name"]} / {self.publish_date_str})')
            else:
                _logger.info(f'Post exists: {self.name}')


class Hub(Base):
    def __init__(self, name, hid, period, nextcall, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.hid = hid
        self.period = period
        self.nextcall = nextcall

    async def run(self):
        await self.set_content()
        post_articles = self.content.find_all("article", {"class": "post post_preview"})
        _logger.info(f'Hub: {self.name}. Found: {len(post_articles)} posts')
        for p_article in post_articles:
            await queue.put(
                Post(url=p_article.h2.a['href'],
                     hub_id=self.hid,
                     )
            )

    async def set_db_nextcall(self):
        nextcall = datetime.datetime.now(tz=pytz.utc).strftime(DATETIME_FORMAT)
        async with database.Database() as db:
            await db.execute(f"""UPDATE habr_hub SET nextcall = '{nextcall}' WHERE id = {self.hid}""")


class Parser:
    async def get_hubs(self):
        hubs = []
        async with database.Database() as db:
            result = await db.fetch(f"""SELECT * FROM habr_hub""")
        now = datetime.datetime.now(tz=pytz.UTC)
        for res in result:
            period = res['period']
            nextcall = res['nextcall']
            nextcall_datetime = datetime.datetime(
                year=nextcall.year,
                month=nextcall.month,
                day=nextcall.day,
                hour=nextcall.hour,
                minute=nextcall.minute,
                second=nextcall.second,
                tzinfo=pytz.UTC,
            )
            if (nextcall_datetime + datetime.timedelta(minutes=period)) > now:
                continue
            hub = Hub(name=res['name'],
                      hid=res['id'],
                      period=period,
                      nextcall=nextcall,
                      url=res['url'],
                      )
            await hub.set_content()
            hubs.append(hub)

        return hubs

    async def run(self):
        while 1:
            hubs = await self.get_hubs()
            for hub in hubs:
                await queue.put(hub)
            tasks = []
            while not queue.empty() and hubs:
                await asyncio.sleep(1)
                while not queue.empty() and len(asyncio.all_tasks()) <= max_parallel:
                    queue_element = await queue.get()
                    tasks.append(asyncio.ensure_future(queue_element.run()))
                try:
                    await asyncio.gather(*tasks)
                except Exception as err:
                    _logger.error(err)
                    continue
                tasks = []
            for hub in hubs:
                await hub.set_db_nextcall()

            await asyncio.sleep(60)

import asyncio
import aiohttp

from bs4 import BeautifulSoup

URL = 'https://habr.com'

async def get_content(url):
    print('get_content')
    # timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.read()
    soup = BeautifulSoup(html, features='lxml')
    posts = soup.find_all("article", {"class": "post post_preview"})
    for p in posts[:5]:
        print(p.h2.a.string)
        print('='*100)
    print('\n\n\n\n')
    # await asyncio.sleep(10)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(get_content(URL))
    loop.run_forever()

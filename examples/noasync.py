import urllib.request
from bs4 import BeautifulSoup

URL = 'https://habr.com'

resp = urllib.request.urlopen(URL)
html = resp.read()

soup = BeautifulSoup(html, features='lxml')
# print(soup)
posts = soup.find_all("article", {"class": "post post_preview"})
post_urls = []

for p in posts:
    post_urls.append(p.h2.a['href'])

for p_url in post_urls:
    resp = urllib.request.urlopen(p_url)
    html = resp.read()
    soup = BeautifulSoup(html, features='lxml')
    post_info = soup.find('article')
    print(post_info.header.a.find('span', {'class': 'user-info__nickname'}).string)

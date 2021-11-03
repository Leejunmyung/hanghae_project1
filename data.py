import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dbsparta_plus

def get_urls():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://movie.naver.com/movie/running/current.naver', headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    lis = soup.select('#content > div.article > div:nth-child(1) > div.lst_wrap > ul > li')

    urls = []
    for li in lis:
        a = li.select_one('dl > dt > a')
        if a is not None:
            base_url = 'https://movie.naver.com/'
            url = base_url + a['href']
            urls.append(url)

    return urls

def insert_movie(url):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    name = soup.select_one('#content > div.article > div.mv_info_area > div.mv_info > h3 > a').text
    img_url = soup.select_one('#content > div.article > div.mv_info_area > div.poster > a > img')['src']
    star = soup.select_one('#actualPointPersentBasic > div > span > span').text
    info = soup.select_one('#content > div.article > div.mv_info_area > div.mv_info > dl > dd:nth-child(2) > p').text
    director = soup.select_one('#content > div.article > div.mv_info_area > div.mv_info > dl > dd:nth-child(4) > p > a').text
    summary = soup.select_one('#content > div.article > div.section_group.section_group_frst > div:nth-child(1) > div > div > p').text

    doc = {
        'name': name,
        'img_url': img_url,
        'star': star,
        'info': info,
        'director': director,
        'summary': summary
    }

    db.movies.insert_one(doc)
    print('완료', name)

def insert_all():
    db.movies.drop()
    urls = get_urls()
    for url in urls:
        insert_movie(url)


insert_all()
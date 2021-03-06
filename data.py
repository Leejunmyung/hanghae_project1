import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dbsparta_plus

# url 크롤링 함수
def get_urls():
    # headers 에 유저정보 담기
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    # data 에 url정보 requests로 받아오기
    data = requests.get('https://movie.naver.com/movie/running/current.naver', headers=headers)

    # bs4로 data 가공
    soup = BeautifulSoup(data.text, 'html.parser')

    # 경로 설정
    lis = soup.select('#content > div.article > div:nth-child(1) > div.lst_wrap > ul > li')

    urls = []
    # 경로를 찾아서 반복문 작성
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

    # 변수들이 None이 아닐때 크롤링해온다.
    a = soup.select_one('#content > div.article > div.section_group.section_group_frst > div:nth-child(4) > div > ul > li:nth-child(1) > a')
    b = soup.select_one('#content > div.article > div.mv_info_area > div.mv_info > dl > dd:nth-child(8) > p > a')
    c = soup.select_one('#content > div.article > div.mv_info_area > div.mv_info > dl > dd:nth-child(10) > div > p.count')
    if a and b and c is not None:
        base_url = 'https://movie.naver.com'
        trailer = base_url + a['href']
        name = soup.select_one('#content > div.article > div.mv_info_area > div.mv_info > h3 > a').text
        img_url = soup.select_one('#content > div.article > div.mv_info_area > div.poster > a > img')['src']
        star = soup.select_one('#actualPointPersentBasic > div > span > span').text
        genre = soup.select_one('#content > div.article > div.mv_info_area > div.mv_info > dl > dd:nth-child(2) > p > span:nth-child(1)').text
        dates = soup.select_one('#content > div.article > div.mv_info_area > div.mv_info > dl > dd:nth-child(2) > p > span:nth-child(4)').text
        time = soup.select_one('#content > div.article > div.mv_info_area > div.mv_info > dl > dd:nth-child(2) > p > span:nth-child(3)').text
        country = soup.select_one('#content > div.article > div.mv_info_area > div.mv_info > dl > dd:nth-child(2) > p > span:nth-child(2) > a').text
        age = b.text
        people = c.text
        actor = soup.select_one('#content > div.article > div.mv_info_area > div.mv_info > dl > dd:nth-child(6) > p').text
        director = soup.select_one('#content > div.article > div.mv_info_area > div.mv_info > dl > dd:nth-child(4) > p > a').text
        summary = soup.select_one('#content > div.article > div.section_group.section_group_frst > div:nth-child(1) > div > div > p').text

        # doc 변수에 키와 벨류값으로 저장
        doc = {
            'name': name,
            'img_url': img_url,
            'star': star,
            'trailer': trailer,
            'genre': genre,
            'dates': dates,
            'time': time,
            'country': country,
            'age': age,
            'people': people,
            'actor': actor,
            'director': director,
            'summary': summary
        }

        # 영화목록 db에 넣어준다.
        db.hangmovies.insert_one(doc)
        print('완료', name)

def insert_all():
    db.hangmovies.drop()
    urls = get_urls()
    for url in urls:
        insert_movie(url)


insert_all()
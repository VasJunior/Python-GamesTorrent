import pymysql
from urllib.request import urlopen,Request
from bs4 import BeautifulSoup
import re

reqHeaders = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                            'AppleWebKit/537.11 (KHTML, like Gecko) '
                            'Chrome/23.0.1271.64 Safari/537.11',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
              'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
              'Accept-Encoding': 'none',
              'Accept-Language': 'en-US,en;q=0.8',
              'Connection': 'keep-alive'}

conn = pymysql.connect(host='127.0.0.1',
                       user='root',
                       passwd='',
                       db='mysql',
                       charset='utf8')

def makeSoup(innerCont):
    req = Request(url=f'https://torrentgamespc.net/category/iso/page/{innerCont}/', headers=reqHeaders)
    url = urlopen(req)
    soup = BeautifulSoup(url, 'lxml')
    return soup

def makeGameSoup(page):
    req = Request(url=page, headers=reqHeaders)
    url = urlopen(req) #abre o Html do request acima.
    soup = BeautifulSoup(url, 'lxml') #faz uma sopa do Html acima.
    return soup #retorna a sopa.

def getTitle(soup):
    title = soup.find('title')
    title = str(title)
    if title.count('-') > 1:
        try:
            title = title[title.index('-',0,17)+2:title.index('-',18)-1]
        except:
            title = title[title.index('>') + 1:title.index('-') - 1]
    else:
        title = title[title.index('>') + 1:title.index('-') - 1]
    return title

def getMag(soup):
    link = None
    mag = soup.find_all('a', style='color: #339966;')
    for m in mag:
        link = m.attrs['href']
    return link

def store(title,url,mag):
    cur.execute(f'INSERT INTO todosjogos (title,mag,url) VALUES ("{title}","{mag}","{url}");')
    cur.connection.commit()
    print(f'Adicionado {title}, no seu DB')

def getPages():
    innerCont = 1
    while innerCont <= getLastPage():
        print(f'Minerando pagina {innerCont}')
        soup = makeSoup(innerCont)
        archive = soup.find('div', class_='post-listing archive-box')
        postBox = archive.find_all('h2', class_='post-box-title')
        for post in postBox:
            a = post.find('a')
            page = a.attrs['href']
            if page not in games:
                innerSoup = makeGameSoup(page)
                title = getTitle(innerSoup)
                mag = getMag(innerSoup)
                store(title,page,mag)
            else:
                print('Já possui esse Jogo')
        innerCont += 1
def getLastPage():
    soup = makeSoup(1)
    last = soup.find('a', class_='last')
    conteudo = last.attrs['href']
    return int(re.sub('[^0-9]', '', conteudo))

cur = conn.cursor()
cur.execute('USE jogostorrent')
cur.execute('SELECT url FROM todosjogos')
pages = cur.fetchall()
games = set()
for page in pages:
    games.add(page[0])
getPages()
cur.close()
conn.close()

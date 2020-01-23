import pymysql
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import re

def makeSoup(innerCont, reqHeaders):
    req = Request(url=f'https://torrentgamespc.net/category/iso/page/{innerCont}/', headers=reqHeaders)
    url = urlopen(req)
    soup = BeautifulSoup(url, 'lxml')
    return soup

def makeGameSoup(page, reqHeaders):
    req = Request(url=page, headers=reqHeaders)
    url = urlopen(req) #abre o Html do request acima.
    soup = BeautifulSoup(url, 'lxml') #faz uma sopa do Html acima.
    return soup #retorna a sopa.

def getTitle(soup):
    title = soup.find('title') # get the element <title>, as we only have 1 of that, there shouldn't have problem;
    #Ex: <title>MechWarrior 5 Mercenaries - PC 2019 CODEX - Games Jogos ISO 2019 2020</title>
    title = str(title) # turns title into a string, and puts it in a var
    if title.count('-') > 1: # if the count of '-' are more than 1
        try:
            t = title[title.index('-',0,17)+2:title.index('-',18)-1] # cut title between the first '-' and the second '-'
            # but here we have a problem: in the case of title be like that: if the title is too short the games titles will be imprecise
            # in this case 'OSK - PC 2019 SKIDROW - Games Jogos ISO 2019 2020'; title will be like that 'PC 2019 SKIDROW'
            if t.__contains__("PC"): # verify if the problem above occurred
                title = title[title.index('>') + 1:title.index('-') - 1] # make the short verification
            else:
                title = t # if the problem not occurred title receive t
        except:
            title = title[title.index('>') + 1:title.index('-') - 1] # short verification
    else: # in this case we have '-' more than one time
        title = title[title.index('>') + 1:title.index('-') - 1] # cut title in '>' of element <title>, and cut on the first '-'
    return title

def getMag(soup):
    link = None
    mag = soup.find_all('a', style='color: #339966;')
    for m in mag:
        link = m.attrs['href']
    return link

def store(title,url,mag, cur):
    cur.execute(f'INSERT INTO todosjogos (title,mag,url) VALUES ("{title}","{mag}","{url}");')
    cur.connection.commit()
    print(f'Adicionado {title}, no seu DB')

def getPages(reqHeaders, cur, games):
    innerCont = 1
    while innerCont <= getLastPage(reqHeaders):
        print(f'Minerando pagina {innerCont}')
        soup = makeSoup(innerCont, reqHeaders)
        archive = soup.find('div', class_='post-listing archive-box')
        postBox = archive.find_all('h2', class_='post-box-title')
        for post in postBox:
            a = post.find('a')
            page = a.attrs['href']
            if page not in games:
                innerSoup = makeGameSoup(page, reqHeaders)
                title = getTitle(innerSoup)
                mag = getMag(innerSoup)
                store(title,page,mag, cur)
            else:
                print(f'({getTitle(makeGameSoup(page,reqHeaders))}) - Já possui esse Jogo')
        innerCont += 1
def getLastPage(reqHeaders):
    soup = makeSoup(1,reqHeaders)
    last = soup.find('a', class_='last')
    conteudo = last.attrs['href']
    return int(re.sub('[^0-9]', '', conteudo))


def main():

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

    cur = conn.cursor()
    cur.execute('USE jogostorrent')
    cur.execute('SELECT url FROM todosjogos')
    pages = cur.fetchall()
    games = set()
    for page in pages:
        games.add(page[0])
    getPages(reqHeaders, cur, games)
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
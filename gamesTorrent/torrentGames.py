from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import re
import pymysql

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


def makeSoup(innerCont): #recebe como parametro a pagina que será minerada
    req = Request(url=f'https://torrentgamespc.net/category/iso/page/{innerCont}/', headers=reqHeaders) #realiza um request da pagina passada, com os Headers Globais
    url = urlopen(req) #abre o Html do request acima.
    soup = BeautifulSoup(url, 'lxml') #faz uma sopa do Html acima.
    return soup #retorna a sopa.

def makeGameSoup(page):
    req = Request(url=page, headers=reqHeaders)
    url = urlopen(req) #abre o Html do request acima.
    soup = BeautifulSoup(url, 'lxml') #faz uma sopa do Html acima.
    return soup #retorna a sopa.



def getLastPage():
    soup = makeSoup(1) #cria uma sopa da primeira pagina, apenas para minerar a quantidade total de paginas
    last = soup.find('a', class_='last') #encontra uma tag 'a' de classe 'last'
    conteudo = last.attrs['href'] #pega o conteudo do atributo 'href' da variavel last, e coloca no conteudo.
    return int(re.sub('[^0-9]', '', conteudo)) #usa uma regularExpression para retornar apenas os numeros da variavel conteudo.

def getPages():
    innerCont = getLastPage() #um contador, ele simboliza a pagina atual que esta sendo minerada
    pages = set() #criação da lista de paginas
    while innerCont >= 1: #cria um laço que ira desde a ultima pagina para a 1
        print(f'Minerando Pagina {innerCont}') #exibe na tela a pagina que atualmente está sendo minerada.
        soup = makeSoup(innerCont) #Faz a sopa com a pagina atual.
        archive = soup.find('div', class_='post-listing archive-box') #acha o artigo que contem os jogos
        postBox = archive.find_all('h2', class_='post-box-title') #acha todos os Jogos da pagina
        for post in reversed(postBox): #pra cada jogo encontrado, detalhe ele ta indo de baixo pra cima, na ordem de postagem.
            a = post.find('a') #encontra a tag 'a' do jogo
            page = a.attrs['href'] #coloca na variavel page o link do jogo
            if page not in pages: #faz uma checagem pelo jogo na lista, se não houver registro, um novo é criado.
                innerSoup = makeGameSoup(page)
                url = page
                title = getTitle(innerSoup)
                mag = getMag(innerSoup)
                pages.add(page) #criando a pagina do jogo na lista.
                store(title,url,mag)
        innerCont -= 1
    return pages

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

def testeConn():
    cur.execute('SELECT * FROM pages')
    print(cur.fetchone())
    cur.close()
    conn.close()

def store(title,url,mag):
    cur.execute(f'INSERT INTO todosjogos (title,mag,url) VALUES ("{title}","{mag}","{url}");')
    cur.connection.commit()
    print(f'Adicionado {title}, no seu DB')

getPages()

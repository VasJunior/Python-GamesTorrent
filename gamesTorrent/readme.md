# GAMES TORRENT
  _A data collector algorithm, it will collect magnetic links from a specific torrent game site;_
  
// **Modules**: <a href="https://mega.nz/#!PdVBQQrB!CpY3g7vpVxQDQ5VtLxxxgjXKxSrMIbMiocSnDm8scDk">click here</a> to download my venv

* **pymysql** 

    used to make a connection between python and MySQL. used in: main(), store();

* **urlopen and Request from  urllib.request** 
  
    urlopen: pull the HTML from a Request. used in: makeSoup(), makeGameSoup();
    
    Request: Make a request passing Headers from a browser( some websites needs a header to give you the html, without this you may         blocked with 403 ERROR: Forbidden). used in: makeSoup(), makeGameSoup();

* **BeautifulSoup from bs4** 
   
    organizes source code from the page and favor data modeling. used in: makeSoup(), makeGameSoup();

* **re** 

    regular expressions is used to separate numbers from letters. used in: getLastPage()

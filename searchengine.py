import urllib3, certifi
import bs4
import sqlite3
import re

class crawler:
    # Initialize the crawler with the name of database
    def __init__(self,dbname):
        self.con = sqlite3.connect(dbname)
    def __del__(self):
        self.con.close()
    def dbcommit(self):
        self.con.commit()

    # Auxilliary function for getting an entry id and adding
    # it if it's not present
    def getentryid(self,table,field,value,createnew=True):
        cur = self.con.execute(
        "select rowid from {0} where {1} = '{2}'".format(table, field, value))
        res = cur.fetchone()
        if res == None:
            cur = self.con.execute(
            "insert into {0} ({1}) values ('{2}')".format(table, field, value))
            return cur.lastrowid
        else:
            return res[0]

    # Index an individual page
    def addtoindex(self,url,soup):
        if self.isindexed(url): return
        print('Indexing ' + url)

        # Get the individual words
        text = self.gettextonly(soup)
        words = self.separatewords(text)

        # Get the URL id
        urlid = self.getentryid('urllist', 'url', url)

        # Link each word to this url
        for i in range(len(words)):
            word = words[i]
            if word in ignorewords: continue
            wordid = self.getentryid('wordlist', 'word', word)
            self.con.execute("insert into wordlocation(urlid,wordid,location) values ({0},{1},{2}".format(urlid, wordid, i))

    # Extract the text from an HTML page (no tags)
    def gettextonly(self,soup):
        v = soup.string
        if v == None:
            c = soup.contents
            resulttext = ''
            for t in c:
                subtext = self.gettextonly(t)
                resulttext += subtext + '\n'
            return resulttext
        else:
            return v.strip()

    # Separate the words by any non-whitespace character
    def separatewords(self,text):
        splitter = re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s!='']

    # Return true if this url is already indexed
    def isindexed(self,url):
        return False
        # u = self.con.execute('select rowid from urllist where url = {0}'.format(url)).fetchone()
        # if u != None:
        #
        #     # check if it has been crawled (XXX: why?)
        #     v = self.con.execute('select * from wordlocation where urlid={0}'.format(u[0])).fetchone()
        #     if v != None: return True
        # return False

    # Add a link between two pages
    def addlinkref(self,urlFrom,urlTo,linkText):
        pass

    # Starting with a list of pages, do a breadth
    # first search to the given depth, indexing pages
    # as we go


    def crawl(self, pages, depth=2):
        for i in range(depth):
            newpages = set()
            http = urllib3.PoolManager(
                cert_reqs='CERT_REQUIRED', ca_certs = certifi.where())
            for page in pages:
                try:
                    # url = 'http://kiwitobes.com/wiki/Programming_language.html'
                    c = http.request('GET', page)
                except:
                    print('Could not open {0}'.format(page))
                    continue
                soup = bs4.BeautifulSoup(c.read(), 'lxml')
                self.addtoindex(page, soup)

                links = soup('a')
                for link in links:
                    if ('href' in dict(link.attrs)):
                        url = urllib3.parse.urljoin(page, link['href'])
                        if url.find("'") != -1: continue
                        url = url.split('#')[0] # remove location portion
                        if url[0:4] == 'http' and not self.isindexed(url):
                            newpages.add(url)
                        linkText = self.gettextonly(link)
                        self.addlinkref(page, url, linkText)
                self.dbcommit()
            pages = newpages

    # Create the database tables
    def createindextables(self):
        self.con.execute('create table urllist(url)')
        self.con.execute('create table wordlist(word)')
        self.con.execute('create table wordlocation(urlid,wordid,location)')
        self.con.execute('create table link(fromid integer,toid integer)')
        self.con.execute('create table linkwords(wordid,linkid)')
        self.con.execute('create index wordidx on wordlist(word)')
        self.con.execute('create index urlidx on urllist(url)')
        self.con.execute('create index wordurlidx on wordlocation(wordid)')
        self.con.execute('create index urltoidx on link(toid)')
        self.con.execute('create index urlfromidx on link(fromid)')
        self.dbcommit()

# Create a list of words to ignore
ignorewords=set(['the','of','to','and','a','in','is','it'])


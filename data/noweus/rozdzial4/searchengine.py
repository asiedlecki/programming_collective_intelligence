import urllib2
from BeautifulSoup import *
from urlparse import urljoin
from pysqlite2 import dbapi2 as sqlite
import nn
mynet=nn.searchnet('nn.db')

# tworzenie listy wyrazów do zignorowania
ignorewords={'the':1,'of':1,'to':1,'and':1,'a':1,'in':1,'is':1,'it':1}


class crawler:
  # inicjowanie przeszukiwacza przy użyciu nazwy bazy danych
  def __init__(self,dbname):
    self.con=sqlite.connect(dbname)
  
  def __del__(self):
    self.con.close()

  def dbcommit(self):
    self.con.commit()

  # funkcja pomocnicza pobierająca identyfikator wpisu i dodająca 
  # go, jeśli nie istnieje
  def getentryid(self,table,field,value,createnew=True):
    cur=self.con.execute(
    "select rowid from %s where %s='%s'" % (table,field,value))
    res=cur.fetchone()
    if res==None:
      cur=self.con.execute(
      "insert into %s (%s) values ('%s')" % (table,field,value))
      return cur.lastrowid
    else:
      return res[0] 


  # indeksowanie pojedynczej strony
  def addtoindex(self,url,soup):
    if self.isindexed(url): return
    print 'Indeksowanie '+url
  
    # pobranie poszczególnych wyrazów
    text=self.gettextonly(soup)
    words=self.separatewords(text)
    
    # pobranie identyfikatora adresu URL
    urlid=self.getentryid('urllist','url',url)
    
    # połączenie każdego wyrazu z danym adresem URL
    for i in range(len(words)):
      word=words[i]
      if word in ignorewords: continue
      wordid=self.getentryid('wordlist','word',word)
      self.con.execute("insert into wordlocation(urlid,wordid,location) values (%d,%d,%d)" % (urlid,wordid,i))
  

  
  # wyodrębnianie tekstu ze strony HTML (bez znaczników)
  def gettextonly(self,soup):
    v=soup.string
    if v==Null:   
      c=soup.contents
      resulttext=''
      for t in c:
        subtext=self.gettextonly(t)
        resulttext+=subtext+'\n'
      return resulttext
    else:
      return v.strip()

  # oddzielanie wyrazów za pomocą dowolnego znaku innego niż biały
  def separatewords(self,text):
    splitter=re.compile('\\W*')
    return [s.lower() for s in splitter.split(text) if s!='']

    
  # zwrócenie wartości true, jeśli adres URL został już zindeksowany
  def isindexed(self,url):
    return False
  
  # dodanie odnośnika między dwiema stronami
  def addlinkref(self,urlFrom,urlTo,linkText):
    words=self.separateWords(linkText)
    fromid=self.getentryid('urllist','url',urlFrom)
    toid=self.getentryid('urllist','url',urlTo)
    if fromid==toid: return
    cur=self.con.execute("insert into link(fromid,toid) values (%d,%d)" % (fromid,toid))
    linkid=cur.lastrowid
    for word in words:
      if word in ignorewords: continue
      wordid=self.getentryid('wordlist','word',word)
      self.con.execute("insert into linkwords(linkid,wordid) values (%d,%d)" % (linkid,wordid))

  # rozpoczęcie przy użyciu listy stron, wykonanie wyszukiwania
  # wszerz do podanej głębokości oraz indeksowanie stron
  # w trakcie realizowania procesu
  def crawl(self,pages,depth=2):
    for i in range(depth):
      newpages={}
      for page in pages:
        try:
          c=urllib2.urlopen(page)
        except:
          print "Nie można otworzyć %s" % page
          continue
        try:
          soup=BeautifulSoup(c.read())
          self.addtoindex(page,soup)
  
          links=soup('a')
          for link in links:
            if ('href' in dict(link.attrs)):
              url=urljoin(page,link['href'])
              if url.find("'")!=-1: continue
              url=url.split('#')[0]  # usuwanie części lokalizacji
              if url[0:4]=='http' and not self.isindexed(url):
                newpages[url]=1
              linkText=self.gettextonly(link)
              self.addlinkref(page,url,linkText)
  
          self.dbcommit()
        except:
          print "Nie można przeanalizować strony %s" % page

      pages=newpages

  
  # Tworzenie tabel bazy danych
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

  def calculatepagerank(self,iterations=20):
    # czyszczenie bieżących tabel wartości algorytmu PageRank
    self.con.execute('drop table if exists pagerank')
    self.con.execute('create table pagerank(urlid primary key,score)')
    
    # inicjowanie każdego adresu URL z wartością 1 algorytmu PageRank
    for (urlid,) in self.con.execute('select rowid from urllist'):
      self.con.execute('insert into pagerank(urlid,score) values (%d,1.0)' % urlid)
    self.dbcommit()
    
    for i in range(iterations):
      print "Iteracja %d" % (i)
      for (urlid,) in self.con.execute('select rowid from urllist'):
        pr=0.15
        
        # wykonanie pętli dla wszystkich stron odwołujących się do danej strony
        for (linker,) in self.con.execute(
        'select distinct fromid from link where toid=%d' % urlid):
          # uzyskanie wartości algorytmu PageRank strony odwołującej się
          linkingpr=self.con.execute(
          'select score from pagerank where urlid=%d' % linker).fetchone()[0]

          # uzyskanie całkowitej liczby odnośników strony odwołującej się
          linkingcount=self.con.execute(
          'select count(*) from link where fromid=%d' % linker).fetchone()[0]
          pr+=0.85*(linkingpr/linkingcount)
        self.con.execute(
        'update pagerank set score=%f where urlid=%d' % (pr,urlid))
      self.dbcommit()

class searcher:
  def __init__(self,dbname):
    self.con=sqlite.connect(dbname)

  def __del__(self):
    self.con.close()

  def getmatchrows(self,q):
    # łańcuchy służące do zbudowania zapytania
    fieldlist='w0.urlid'
    tablelist=''  
    clauselist=''
    wordids=[]

    # podział wyrazów przy użyciu spacji
    words=q.split(' ')  
    tablenumber=0

    for word in words:
      # pobranie identyfikatora wyrazu
      wordrow=self.con.execute(
      "select rowid from wordlist where word='%s'" % word).fetchone()
      if wordrow!=None:
        wordid=wordrow[0]
        wordids.append(wordid)
        if tablenumber>0:
          tablelist+=','
          clauselist+=' and '
          clauselist+='w%d.urlid=w%d.urlid and ' % (tablenumber-1,tablenumber)
        fieldlist+=',w%d.location' % tablenumber
        tablelist+='wordlocation w%d' % tablenumber      
        clauselist+='w%d.wordid=%d' % (tablenumber,wordid)
        tablenumber+=1

    # tworzenie zapytania przy użyciu osobnych części
    fullquery='select %s from %s where %s' % (fieldlist,tablelist,clauselist)
    print fullquery
    cur=self.con.execute(fullquery)
    rows=[row for row in cur]

    return rows,wordids

  def getscoredlist(self,rows,wordids):
    totalscores=dict([(row[0],0) for row in rows])

    # W tym miejscu zostaną później wstawione funkcje oceniania
    weights=[(1.0,self.locationscore(rows)), 
             (1.0,self.frequencyscore(rows)),
             (1.0,self.pagerankscore(rows)),
             (1.0,self.linktextscore(rows,wordids)),
             (5.0,self.nnscore(rows,wordids))]
    for (weight,scores) in weights:
      for url in totalscores:
        totalscores[url]+=weight*scores[url]

    return totalscores

  def geturlname(self,id):
    return self.con.execute(
    "select url from urllist where rowid=%d" % id).fetchone()[0]

  def query(self,q):
    rows,wordids=self.getmatchrows(q)
    scores=self.getscoredlist(rows,wordids)
    rankedscores=[(score,url) for (url,score) in scores.items()]
    rankedscores.sort()
    rankedscores.reverse()
    for (score,urlid) in rankedscores[0:10]:
      print '%f\t%s' % (score,self.geturlname(urlid))
    return wordids,[r[1] for r in rankedscores[0:10]]

  def normalizescores(self,scores,smallIsBetter=0):
    vsmall=0.00001 # uniknięcie dzielenia przez zero
    if smallIsBetter:
      minscore=min(scores.values())
      return dict([(u,float(minscore)/max(vsmall,l)) for (u,l) in scores.items()])
    else:
      maxscore=max(scores.values())
      if maxscore==0: maxscore=vsmall
      return dict([(u,float(c)/maxscore) for (u,c) in scores.items()])

  def frequencyscore(self,rows):
    counts=dict([(row[0],0) for row in rows])
    for row in rows: counts[row[0]]+=1
    return self.normalizescores(counts)

  def locationscore(self,rows):
    locations=dict([(row[0],1000000) for row in rows])
    for row in rows:
      loc=sum(row[1:])
      if loc<locations[row[0]]: locations[row[0]]=loc
    
    return self.normalizescores(locations,smallIsBetter=1)

  def distancescore(self,rows):
    # Jeśli występuje tylko jeden wyraz, każdy wygrywa!
    if len(rows[0])<=2: return dict([(row[0],1.0) for row in rows])

    # inicjowanie słownika z dużymi wartościami
    mindistance=dict([(row[0],1000000) for row in rows])

    for row in rows:
      dist=sum([abs(row[i]-row[i-1]) for i in range(2,len(row))])
      if dist<mindistance[row[0]]: mindistance[row[0]]=dist
    return self.normalizescores(mindistance,smallIsBetter=1)

  def inboundlinkscore(self,rows):
    uniqueurls=dict([(row[0],1) for row in rows])
    inboundcount=dict([(u,self.con.execute('select count(*) from link where toid=%d' % u).fetchone()[0]) for u in uniqueurls])   
    return self.normalizescores(inboundcount)

  def linktextscore(self,rows,wordids):
    linkscores=dict([(row[0],0) for row in rows])
    for wordid in wordids:
      cur=self.con.execute('select link.fromid,link.toid from linkwords,link where wordid=%d and linkwords.linkid=link.rowid' % wordid)
      for (fromid,toid) in cur:
        if toid in linkscores:
          pr=self.con.execute('select score from pagerank where urlid=%d' % fromid).fetchone()[0]
          linkscores[toid]+=pr
    maxscore=max(linkscores.values())
    normalizedscores=dict([(u,float(l)/maxscore) for (u,l) in linkscores.items()])
    return normalizedscores

  def pagerankscore(self,rows):
    pageranks=dict([(row[0],self.con.execute('select score from pagerank where urlid=%d' % row[0]).fetchone()[0]) for row in rows])
    maxrank=max(pageranks.values())
    normalizedscores=dict([(u,float(l)/maxrank) for (u,l) in pageranks.items()])
    return normalizedscores

  def nnscore(self,rows,wordids):
    # uzyskiwanie unikalnych identyfikatorów adresów URL w postaci uporządkowanej listy
    urlids=[urlid for urlid in dict([(row[0],1) for row in rows])]
    nnres=mynet.getresult(wordids,urlids)
    scores=dict([(urlids[i],nnres[i]) for i in range(len(urlids))])
    return self.normalizescores(scores)

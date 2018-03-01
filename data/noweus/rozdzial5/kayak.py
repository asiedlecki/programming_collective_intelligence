import time
import urllib2
import xml.dom.minidom

kayakkey='WSTAW_TUTAJ_KLUCZ'

def getkayaksession():
  # tworzenie adresu URL w celu rozpoczęcia sesji
  url='http://www.kayak.com/k/ident/apisession?token=%s&version=1' % kayakkey
  
  # analizowanie uzyskanych danych XML
  doc=xml.dom.minidom.parseString(urllib2.urlopen(url).read())
  
  # znajdowanie identyfikatora <sid>xxxxxxxx</sid>
  sid=doc.getElementsByTagName('sid')[0].firstChild.data
  return sid

def flightsearch(sid,origin,destination,depart_date):
  
  # tworzenie adresu URL wyszukiwania
  url='http://www.kayak.com/s/apisearch?basicmode=true&oneway=y&origin=%s' % origin
  url+='&destination=%s&depart_date=%s' % (destination,depart_date)
  url+='&return_date=none&depart_time=a&return_time=a'
  url+='&travelers=1&cabin=e&action=doFlights&apimode=1'
  url+='&_sid_=%s&version=1' % (sid)

  # uzyskanie danych XML
  doc=xml.dom.minidom.parseString(urllib2.urlopen(url).read())

  # wyodrębnienie identyfikatora wyszukiwania
  searchid=doc.getElementsByTagName('searchid')[0].firstChild.data

  return searchid

def flightsearchresults(sid,searchid):
  def parseprice(p): 
    return float(p[1:].replace(',',''))

  # pętla odpytywania
  while 1:
    time.sleep(2)

    # tworzenie adresu URL na potrzeby odpytywania
    url='http://www.kayak.com/s/basic/flight?'
    url+='searchid=%s&c=5&apimode=1&_sid_=%s&version=1' % (searchid,sid)
    doc=xml.dom.minidom.parseString(urllib2.urlopen(url).read())

    # szukanie znacznika morepending i oczekiwanie do momentu, aż nie będzie mieć wartości true
    morepending=doc.getElementsByTagName('morepending')[0].firstChild
    if morepending==None or morepending.data=='false': break

  # pobranie kompletnej listy
  url='http://www.kayak.com/s/basic/flight?'
  url+='searchid=%s&c=999&apimode=1&_sid_=%s&version=1' % (searchid,sid)
  doc=xml.dom.minidom.parseString(urllib2.urlopen(url).read())

  # uzyskiwanie różnych elementów jako list
  prices=doc.getElementsByTagName('price')
  departures=doc.getElementsByTagName('depart')
  arrivals=doc.getElementsByTagName('arrive')  

  # połączenie elementów ze sobą
  return zip([p.firstChild.data.split(' ')[1] for p in departures],
             [p.firstChild.data.split(' ')[1] for p in arrivals],
             [parseprice(p.firstChild.data) for p in prices])


def createschedule(people,dest,dep,ret):
  # uzyskanie identyfikatora sesji dla wyszukiwań
  sid=getkayaksession()
  flights={}
  
  for p in people:
    name,origin=p
    # przylot
    searchid=flightsearch(sid,origin,dest,dep)
    flights[(origin,dest)]=flightsearchresults(sid,searchid)
    
    # lot powrotny
    searchid=flightsearch(sid,dest,origin,ret)
    flights[(dest,origin)]=flightsearchresults(sid,searchid)
    
  return flights

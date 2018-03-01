import urllib2
import xml.dom.minidom

api_key='W tym miejscu Twój klucz interfejsu API'

def getrandomratings(c):
  # tworzenie adresu URL dla metody getRandomProfilee
  url="http://services.hotornot.com/rest/?app_key=%s" % api_key
  url+="&method=Rate.getRandomProfile&retrieve_num=%d" % c
  url+="&get_rate_info=true&meet_users_only=true"
  
  f1=urllib2.urlopen(url).read()

  doc=xml.dom.minidom.parseString(f1)
  
  emids=doc.getElementsByTagName('emid')
  ratings=doc.getElementsByTagName('rating')

  # łączenie identyfikatorów emid i ocen do postaci listy
  result=[]
  for e,r in zip(emids,ratings):
    if r.firstChild!=None:
      result.append((e.firstChild.data,r.firstChild.data))
  return result

stateregions={'Nowa Anglia':['ct','mn','ma','nh','ri','vt'],
              'Środkowoatlantycki':['de','md','nj','ny','pa'],
              'Południowy':['al','ak','fl','ga','ky','la','ms','mo',
                       'nc','sc','tn','va','wv'],
              'Środkowozachodni':['il','in','ia','ks','mi','ne','nd','oh','sd','wi'],
              'Zachodni':['ak','ca','co','hi','id','mt','nv','or','ut','wa','wy']}

def getpeopledata(ratings):
  result=[]
  for emid,rating in ratings:
    # adres URL dla metody MeetMe.getProfile
    url="http://services.hotornot.com/rest/?app_key=%s" % api_key
    url+="&method=MeetMe.getProfile&emid=%s&get_keywords=true" % emid

    # uzyskanie wszystkich informacji o danej osobie
    try:
      rating=int(float(rating)+0.5)
      doc2=xml.dom.minidom.parseString(urllib2.urlopen(url).read())
      gender=doc2.getElementsByTagName('gender')[0].firstChild.data
      age=doc2.getElementsByTagName('age')[0].firstChild.data
      loc=doc2.getElementsByTagName('location')[0].firstChild.data[0:2]

      # przekształcenie stanu w region
      for r,s in stateregions.items():
        if loc in s: region=r

      if region!=None:
        result.append((gender,int(age),region,rating))
    except:
      pass
  return result


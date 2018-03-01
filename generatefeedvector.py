import feedparser
import re

# Zwraca tytuł i słownik liczby wyrazów dla kanału informacyjnego RSS.
def getwordcounts(url):
  # analizowanie kanału informacyjnego
  d=feedparser.parse(url)
  wc={}

  # przetwarzanie w pętli wszystkich wpisów
  for e in d.entries:
    if 'summary' in e: summary=e.summary
    else: summary=e.description

    # wyodrębnianie listy wyrazów
    words=getwords(e.title+' '+summary)
    for word in words:
      wc.setdefault(word,0)
      wc[word]+=1
  return d.feed.title,wc

def getwords(html):
  # usuwanie wszystkich znaczników HTML
  txt=re.compile(r'<[^>]+>').sub('',html)

  # podział wyrazów przy użyciu wszystkich znaków niealfabetycznych
  words=re.compile(r'[^A-Z^a-z]+').split(txt)

  # konwersja na małe litery
  return [word.lower() for word in words if word!='']


apcount={}
wordcounts={}
feedlist=[line for line in open('data/noweus/rozdzial3/feedlist.txt')]
for feedurl in feedlist:
  try:
    title,wc=getwordcounts(feedurl)
    wordcounts[title]=wc
    for word,count in wc.items():
      apcount.setdefault(word,0)
      if count>1:
        apcount[word]+=1
  except:
    print('Nie powiodła się analiza kanału informacyjnego {0}'.format(feedurl))

wordlist=[]
for w,bc in apcount.items():
  frac=float(bc)/len(feedlist)
  if frac>0.1 and frac<0.5:
    wordlist.append(w)

out=open('blogdata.txt','w')
out.write('Blog')
for word in wordlist: out.write('\t{0}'.format(word))
out.write('\n')
for blog,wc in wordcounts.items():
  print(blog)
  out.write(blog)
  for word in wordlist:
    if word in wc: out.write('\t{0}'.format(wc[word]))
    else: out.write('\t0')
  out.write('\n')
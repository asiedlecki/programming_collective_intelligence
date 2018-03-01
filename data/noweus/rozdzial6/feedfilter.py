import feedparser
import re

# pobranie nazwy pliku z adresu URL kanału informacyjnego bloga i sklasyfikowanie wpisów
def read(feed,classifier):
  # pobranie wpisów kanału informacyjnego i wykonanie dla nich pętli
  f=feedparser.parse(feed)
  for entry in f['entries']:
    print
    print '-----'
    # wyświetlenie treści wpisu
    print 'Tytuł:     '+entry['title'].encode('utf-8')
    print 'Publikujący: '+entry['publisher'].encode('utf-8')
    print
    print entry['summary'].encode('utf-8')
    

    # połączenie całego tekstu w celu utworzenia jednego elementu dla klasyfikatora 
    fulltext='%s\n%s\n%s' % (entry['title'],entry['publisher'],entry['summary'])

    # połączenie całego tekstu w celu utworzenia jednego elementu dla klasyfikatora 
    print 'Założenie: '+str(classifier.classify(entry))

    # poproszenie użytkownika o podanie poprawnej kategorii i przeprowadzenie dla niej treningu
    cl=raw_input('Wprowadź kategorię: ')
    classifier.train(entry,cl)


def entryfeatures(entry):
  splitter=re.compile('\\W*')
  f={}
  
  # wyodrębnianie wyrazów tytułu i tworzenie adnotacji
  titlewords=[s.lower() for s in splitter.split(entry['title']) 
          if len(s)>2 and len(s)<20]
  for w in titlewords: f['Tytuł:'+w]=1
  
  # wyodrębnianie wyrazów podsumowania
  summarywords=[s.lower() for s in splitter.split(entry['summary']) 
          if len(s)>2 and len(s)<20]

  # określenie liczby wyrazów z wielkimi literami
  uc=0
  for i in range(len(summarywords)):
    w=summarywords[i]
    f[w]=1
    if w.isupper(): uc+=1
    
    # uzyskanie par wyrazów w podsumowaniu jako właściwości
    if i<len(summarywords)-1:
      twowords=' '.join(summarywords[i:i+1])
      f[twowords]=1
    
  # zachowanie w całości informacji o twórcy i publikującym
  f['Publikujący:'+entry['publisher']]=1

  # UPPERCASE to wirtualny wyraz oznaczający zbyt krzykliwy styl  
  if float(uc)/len(summarywords)>0.3: f['UPPERCASE']=1
  
  return f

my_data=[['slashdot','Stany Zjednoczone','tak',18,'Brak'],
        ['google','Francja','tak',23,'Rozbudowana'],
        ['digg','Stany Zjednoczone','tak',24,'Podstawowa'],
        ['kiwitobes','Francja','tak',23,'Podstawowa'],
        ['google','Wielka Brytania','nie',21,'Rozbudowana'],
        ['(bezpośrednio)','Nowa Zelandia','nie',12,'Brak'],
        ['(bezpośrednio)','Wielka Brytania','nie',21,'Podstawowa'],
        ['google','Stany Zjednoczone','nie',24,'Rozbudowana'],
        ['slashdot','Francja','tak',19,'Brak'],
        ['digg','Stany Zjednoczone','nie',18,'Brak'],
        ['google','Wielka Brytania','nie',18,'Brak'],
        ['kiwitobes','Wielka Brytania','nie',19,'Brak'],
        ['digg','Nowa Zelandia','tak',12,'Podstawowa'],
        ['slashdot','Wielka Brytania','nie',21,'Brak'],
        ['google','Wielka Brytania','tak',18,'Podstawowa'],
        ['kiwitobes','Francja','tak',19,'Podstawowa']]

class decisionnode:
  def __init__(self,col=-1,value=None,results=None,tb=None,fb=None):
    self.col=col
    self.value=value
    self.results=results
    self.tb=tb
    self.fb=fb

# Podział zbioru na podstawie określonej kolumny. Możliwa jest obsługa wartości
# liczbowych lub nominalnych.
def divideset(rows,column,value):
   # tworzenie funkcji określającej, czy wiersz znajduje się 
   # w pierwszej (true), czy w drugiej grupie (false)
   split_function=None
   if isinstance(value,int) or isinstance(value,float):
      split_function=lambda row:row[column]>=value
   else:
      split_function=lambda row:row[column]==value
   
   # podział wierszy na dwa zbiory i zwrócenie ich
   set1=[row for row in rows if split_function(row)]
   set2=[row for row in rows if not split_function(row)]
   return (set1,set2)


# określanie liczb wystąpień możliwych wyników (ostatnia kolumna 
# każdego wiersza to wynik)
def uniquecounts(rows):
   results={}
   for row in rows:
      # Wynikiem jest ostatnia kolumna.
      r=row[len(row)-1]
      if r not in results: results[r]=0
      results[r]+=1
   return results

# prawdopodobieństwo tego, że losowo umieszczony element
# znajdzie się w niepoprawnej kategorii
def giniimpurity(rows):
  total=len(rows)
  counts=uniquecounts(rows)
  imp=0
  for k1 in counts:
    p1=float(counts[k1])/total
    for k2 in counts:
      if k1==k2: continue
      p2=float(counts[k2])/total
      imp+=p1*p2
  return imp

# Entropia jest sumą iloczynów p(x)log(p(x)) dla wszystkich 
# różnych możliwych wyników.
def entropy(rows):
   from math import log
   log2=lambda x:log(x)/log(2)  
   results=uniquecounts(rows)
   # obliczenie entropii
   ent=0.0
   for r in results.keys():
      p=float(results[r])/len(rows)
      ent=ent-p*log2(p)
   return ent




def printtree(tree,indent=''):
   # Czy to jest węzeł liścia?
   if tree.results!=None:
      print str(tree.results)
   else:
      # wyświetlenie kryteriów
      print str(tree.col)+':'+str(tree.value)+'? '

      # wyświetlenie gałęzi
      print indent+'T->',
      printtree(tree.tb,indent+'  ')
      print indent+'F->',
      printtree(tree.fb,indent+'  ')


def getwidth(tree):
  if tree.tb==None and tree.fb==None: return 1
  return getwidth(tree.tb)+getwidth(tree.fb)

def getdepth(tree):
  if tree.tb==None and tree.fb==None: return 0
  return max(getdepth(tree.tb),getdepth(tree.fb))+1


from PIL import Image,ImageDraw

def drawtree(tree,jpeg='tree.jpg'):
  w=getwidth(tree)*100
  h=getdepth(tree)*100+120

  img=Image.new('RGB',(w,h),(255,255,255))
  draw=ImageDraw.Draw(img)

  drawnode(draw,tree,w/2,20)
  img.save(jpeg,'JPEG')
  
def drawnode(draw,tree,x,y):
  if tree.results==None:
    # uzyskanie szerokości każdej gałęzi
    w1=getwidth(tree.fb)*100
    w2=getwidth(tree.tb)*100

    # określenie całkowitego miejsca wymaganego przez dany węzeł
    left=x-(w1+w2)/2
    right=x+(w1+w2)/2

    # rysowanie łańcucha warunku
    draw.text((x-20,y-10),str(tree.col)+':'+str(tree.value),(0,0,0))

    # rysowanie łączy z gałęziami
    draw.line((x,y,left+w1/2,y+100),fill=(255,0,0))
    draw.line((x,y,right-w2/2,y+100),fill=(255,0,0))
    
    # rysowanie węzłów gałęzi
    drawnode(draw,tree.fb,left+w1/2,y+100)
    drawnode(draw,tree.tb,right-w2/2,y+100)
  else:
    txt=' \n'.join(['%s:%d'%v for v in tree.results.items()])
    draw.text((x-20,y),txt,(0,0,0))


def classify(observation,tree):
  if tree.results!=None:
    return tree.results
  else:
    v=observation[tree.col]
    branch=None
    if isinstance(v,int) or isinstance(v,float):
      if v>=tree.value: branch=tree.tb
      else: branch=tree.fb
    else:
      if v==tree.value: branch=tree.tb
      else: branch=tree.fb
    return classify(observation,branch)

def prune(tree,mingain):
  # Jeśli gałęzie nie są liśćmi, zostaną przycięte.
  if tree.tb.results==None:
    prune(tree.tb,mingain)
  if tree.fb.results==None:
    prune(tree.fb,mingain)
    
  # Jeśli obie podgałęzie są teraz liśćmi, należy sprawdzić, czy
  # powinny zostać scalone.
  if tree.tb.results!=None and tree.fb.results!=None:
    # utworzenie połączonego zbioru danych
    tb,fb=[],[]
    for v,c in tree.tb.results.items():
      tb+=[[v]]*c
    for v,c in tree.fb.results.items():
      fb+=[[v]]*c
    
    # testowanie zmniejszenia entropii
    delta=entropy(tb+fb)-(entropy(tb)+entropy(fb)/2)

    if delta<mingain:
      # scalanie gałęzi
      tree.tb,tree.fb=None,None
      tree.results=uniquecounts(tb+fb)

def mdclassify(observation,tree):
  if tree.results!=None:
    return tree.results
  else:
    v=observation[tree.col]
    if v==None:
      tr,fr=mdclassify(observation,tree.tb),mdclassify(observation,tree.fb)
      tcount=sum(tr.values())
      fcount=sum(fr.values())
      tw=float(tcount)/(tcount+fcount)
      fw=float(fcount)/(tcount+fcount)
      result={}
      for k,v in tr.items(): result[k]=v*tw
      for k,v in fr.items(): result[k]=v*fw      
      return result
    else:
      if isinstance(v,int) or isinstance(v,float):
        if v>=tree.value: branch=tree.tb
        else: branch=tree.fb
      else:
        if v==tree.value: branch=tree.tb
        else: branch=tree.fb
      return mdclassify(observation,branch)

def variance(rows):
  if len(rows)==0: return 0
  data=[float(row[len(row)-1]) for row in rows]
  mean=sum(data)/len(data)
  variance=sum([(d-mean)**2 for d in data])/len(data)
  return variance

def buildtree(rows,scoref=entropy):
  if len(rows)==0: return decisionnode()
  current_score=scoref(rows)

  # skonfigurowanie zmiennych do śledzenia najlepszych kryteriów
  best_gain=0.0
  best_criteria=None
  best_sets=None
  
  column_count=len(rows[0])-1
  for col in range(0,column_count):
    # generowanie listy różnych wartości w
    # tej kolumnie
    column_values={}
    for row in rows:
       column_values[row[col]]=1
    # próba podziału wierszy dla każdej wartości
    # w tej kolumnie
    for value in column_values.keys():
      (set1,set2)=divideset(rows,col,value)
      
      # przyrost informacji
      p=float(len(set1))/len(rows)
      gain=current_score-p*scoref(set1)-(1-p)*scoref(set2)
      if gain>best_gain and len(set1)>0 and len(set2)>0:
        best_gain=gain
        best_criteria=(col,value)
        best_sets=(set1,set2)
  # tworzenie podgałęzi   
  if best_gain>0:
    trueBranch=buildtree(best_sets[0])
    falseBranch=buildtree(best_sets[1])
    return decisionnode(col=best_criteria[0],value=best_criteria[1],
                        tb=trueBranch,fb=falseBranch)
  else:
    return decisionnode(results=uniquecounts(rows))

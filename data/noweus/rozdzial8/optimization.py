import time
import random
import math

people = [('Sylwia','BOS'),
          ('Franek','DAL'),
          ('Zofia','CAK'),
          ('Waldek','MIA'),
          ('Bartek','ORD'),
          ('Liza','OMA')]
# lotnisko w Nowym Jorku
destination='LGA'

flights={}
# 
"""
for line in file('schedule.txt'):
  origin,dest,depart,arrive,price=line.strip().split(',')
  flights.setdefault((origin,dest),[])

  # Dodaj szczegóły do listy możliwych lotów
  flights[(origin,dest)].append((depart,arrive,int(price)))
"""
def getminutes(t):
  x=time.strptime(t,'%H:%M')
  return x[3]*60+x[4]

def printschedule(r):
  for d in range(len(r)/2):
    name=people[d][0]
    origin=people[d][1]
    out=flights[(origin,destination)][int(r[d])]
    ret=flights[(destination,origin)][int(r[d+1])]
    print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name,origin,
                                                  out[0],out[1],out[2],
                                                  ret[0],ret[1],ret[2])

def schedulecost(sol):
  totalprice=0
  latestarrival=0
  earliestdep=24*60

  for d in range(len(sol)/2):
    # pobieranie przylotów i lotów powrotnych
    origin=people[d][1]
    outbound=flights[(origin,destination)][int(sol[d])]
    returnf=flights[(destination,origin)][int(sol[d+1])]
    
    # łączna cena to cena wszystkich przylotów i lotów powrotnych
    totalprice+=outbound[2]
    totalprice+=returnf[2]
    
    # określenie najpóźniejszego przylotu i najwcześniejszego odlotu
    if latestarrival<getminutes(outbound[1]): latestarrival=getminutes(outbound[1])
    if earliestdep>getminutes(returnf[0]): earliestdep=getminutes(returnf[0])
  
  # Każda osoba musi czekać na lotnisku do momentu przybycia ostatniej osoby.
  # Wszystkie osoby muszą też przybyć o jednej porze i czekać na swoje loty.
  totalwait=0  
  for d in range(len(sol)/2):
    origin=people[d][1]
    outbound=flights[(origin,destination)][int(sol[d])]
    returnf=flights[(destination,origin)][int(sol[d+1])]
    totalwait+=latestarrival-getminutes(outbound[1])
    totalwait+=getminutes(returnf[0])-earliestdep  

  # Czy to rozwiązanie wymaga dodatkowego dnia wypożyczenia samochodu? Będzie to kosztować 50 dolarów!
  if latestarrival>earliestdep: totalprice+=50
  
  return totalprice+totalwait

def randomoptimize(domain,costf):
  best=999999999
  bestr=None
  for i in range(0,1000):
    # utworzenie losowego rozwiązania
    r=[float(random.randint(domain[i][0],domain[i][1])) 
       for i in range(len(domain))]
    
    # uzyskanie kosztu
    cost=costf(r)
    
    # porównanie wariantu z najlepszym dotychczasowym
    if cost<best:
      best=cost
      bestr=r 
  return r


def annealingoptimize(domain,costf,T=10000.0,cool=0.95,step=1):
  # losowe inicjowanie wartości
  vec=[float(random.randint(domain[i][0],domain[i][1])) 
       for i in range(len(domain))]
  
  while T>0.1:
    # wybór jednego z indeksów
    i=random.randint(0,len(domain)-1)

    # wybór kierunku do zmiany
    dir=random.randint(-step,step)

    # utworzenie nowej listy z jedną ze zmienionych wartości
    vecb=vec[:]
    vecb[i]+=dir
    if vecb[i]<domain[i][0]: vecb[i]=domain[i][0]
    elif vecb[i]>domain[i][1]: vecb[i]=domain[i][1]

    # obliczenie bieżącego i nowego kosztu
    ea=costf(vec)
    eb=costf(vecb)
    p=pow(math.e,(-eb-ea)/T)

    print vec,ea


    # Czy jest to lepsze rozwiązanie, czy powoduje osiągnięcie
    # górnego limitu prawdopodobieństwa?
    if (eb<ea or random.random()<p):
      vec=vecb      

    # obniżenie temperatury
    T=T*cool
  return vec

def swarmoptimize(domain,costf,popsize=20,lrate=0.1,maxv=2.0,iters=50):
  # Inicjowanie poszczególnych
  # bieżących rozwiązań
  x=[]

  # najlepsze rozwiązania
  p=[]

  # prędkości
  v=[]
  
  for i in range(0,popsize):
    vec=[float(random.randint(domain[i][0],domain[i][1])) 
         for i in range(len(domain))]
    x.append(vec)
    p.append(vec[:])
    v.append([0.0 for i in vec])
  
  
  for ml in range(0,iters):
    for i in range(0,popsize):
      # Najlepsze rozwiązanie dla tej cząstki
      if costf(x[i])<costf(p[i]):
        p[i]=x[i][:]
      g=i

      # Najlepsze rozwiązanie dla dowolnej cząstki
      for j in range(0,popsize):
        if costf(p[j])<costf(p[g]): g=j
      for d in range(len(x[i])):
        # Aktualizuj prędkość tej cząstki
        v[i][d]+=lrate*(p[i][d]-x[i][d])+lrate*(p[g][d]-x[i][d])

        # ogranicz prędkość do maksimum
        if v[i][d]>maxv: v[i][d]=maxv
        elif v[i][d]<-maxv: v[i][d]=-maxv

        # określ granice rozwiązania
        x[i][d]+=v[i][d]
        if x[i][d]<domain[d][0]: x[i][d]=domain[d][0]
        elif x[i][d]>domain[d][1]: x[i][d]=domain[d][1]

    print p[g],costf(p[g])
  return p[g]

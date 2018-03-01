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
for line in file('schedule.txt'):
  origin,dest,depart,arrive,price=line.strip().split(',')
  flights.setdefault((origin,dest),[])

  # dodanie szczegółów do listy potencjalnych lotów
  flights[(origin,dest)].append((depart,arrive,int(price)))

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
    
    # łączna cena to cena wszystkich przylotów ilotów powrotnych
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

def hillclimb(domain,costf):
  # tworzenie losowego rozwiązania
  sol=[random.randint(domain[i][0],domain[i][1])
      for i in range(len(domain))]
  # główna pętla
  while 1:
    # tworzenie listy sąsiednich rozwiązań
    neighbors=[]
    
    for j in range(len(domain)):
      # zwiększanie lub zmniejszanie elementu o 1
      if sol[j]>domain[j][0]:
        neighbors.append(sol[0:j]+[sol[j]+1]+sol[j+1:])
      if sol[j]<domain[j][1]:
        neighbors.append(sol[0:j]+[sol[j]-1]+sol[j+1:])

    # sprawdzenie, jakie jest najlepsze rozwiązanie wśród sąsiednich rozwiązań
    current=costf(sol)
    best=current
    for j in range(len(neighbors)):
      cost=costf(neighbors[j])
      if cost<best:
        best=cost
        sol=neighbors[j]

    # Brak uzyskania lepszego wyniku oznacza osiągnięcie wierzchołka.
    if best==current:
      break
  return sol

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

    # Czy jest to lepsze rozwiązanie, czy powoduje osiągnięcie
    # górnego limitu prawdopodobieństwa?
    if (eb<ea or random.random()<p):
      vec=vecb      

    # obniżenie temperatury
    T=T*cool
  return vec

def geneticoptimize(domain,costf,popsize=50,step=1,
                    mutprod=0.2,elite=0.2,maxiter=100):
  # operacja mutacji
  def mutate(vec):
    i=random.randint(0,len(domain)-1)
    if random.random()<0.5 and vec[i]>domain[i][0]:
      return vec[0:i]+[vec[i]-step]+vec[i+1:] 
    elif vec[i]<domain[i][1]:
      return vec[0:i]+[vec[i]+step]+vec[i+1:]
  
  # operacja krzyżowania
  def crossover(r1,r2):
    i=random.randint(1,len(domain)-2)
    return r1[0:i]+r2[i:]

  # tworzenie początkowej populacji
  pop=[]
  for i in range(popsize):
    vec=[random.randint(domain[i][0],domain[i][1]) 
         for i in range(len(domain))]
    pop.append(vec)
  
  # Ilu wygranych jest w każdej generacji?
  topelite=int(elite*popsize)
  
  # główna pętla 
  for i in range(maxiter):
    scores=[(costf(v),v) for v in pop]
    scores.sort()
    ranked=[v for (s,v) in scores]
    
    # rozpoczęcie od wygranych w czystej postaci
    pop=ranked[0:topelite]
    
    # dodanie zmutowanych i wyhodowanych form wygranych
    while len(pop)<popsize:
      if random.random()<mutprob:

        # mutacja
        c=random.randint(0,topelite)
        pop.append(mutate(ranked[c]))
      else:
      
        # krzyżowanie
        c1=random.randint(0,topelite)
        c2=random.randint(0,topelite)
        pop.append(crossover(ranked[c1],ranked[c2]))
    
    # wyświetlenie najlepszego bieżącego wyniku
    print scores[0][0]
    
  return scores[0][1]

from numpy import *

def difcost(a,b):
  dif=0
  for i in range(shape(a)[0]):
    for j in range(shape(a)[1]):
      # odległość euklidesowa
      dif+=pow(a[i,j]-b[i,j],2)
  return dif

def factorize(v,pc=10,iter=50):
  ic=shape(v)[0]
  fc=shape(v)[1]

  # inicjowanie macierzy wag i właściwości z wartościami losowymi
  w=matrix([[random.random() for j in range(pc)] for i in range(ic)])
  h=matrix([[random.random() for i in range(fc)] for i in range(pc)])

  # wykonanie operacji maksymalną liczbę iteracji
  for i in range(iter):
    wh=w*h
    
    # obliczanie bieżącej różnicy
    cost=difcost(v,wh)
    
    if i%10==0: print cost
    
    # zakończenie w przypadku pełnej faktoryzacji macierzy
    if cost==0: break
    
    # aktualizacja macierzy właściwości
    hn=(transpose(w)*v)
    hd=(transpose(w)*w*h)
  
    h=matrix(array(h)*array(hn)/array(hd))

    # aktualizacja macierzy wag
    wn=(v*transpose(h))
    wd=(w*h*transpose(h))

    w=matrix(array(w)*array(wn)/array(wd))  
    
  return w,h

import random
import math

# akademiki, w których dostępne są po dwa miejsca
dorms=['Zeus','Atena','Herkules','Bachus','Pluton']

# osoby oraz ich pierwsze dwa wybory
prefs=[('Tomasz', ('Bachus', 'Herkules')),
       ('Stefan', ('Zeus', 'Pluton')),
       ('Andrzej', ('Atena', 'Zeus')),
       ('Sara', ('Zeus', 'Pluton')),
       ('Dawid', ('Atena', 'Bachus')),
       ('Jan', ('Herkules', 'Pluton')),
       ('Franek', ('Pluton', 'Atena')),
       ('Sofia', ('Bachus', 'Herkules')),
       ('Laura', ('Bachus', 'Herkules')),
       ('Nikodem', ('Herkules', 'Atena'))]

# [(0,9),(0,8),(0,7),(0,6),...,(0,0)]
domain=[(0,(len(dorms)*2)-i-1) for i in range(0,len(dorms)*2)]

def printsolution(vec):
  slots=[]
  # tworzenie dwóch miejsc dla każdego akademika
  for i in range(len(dorms)): slots+=[i,i]

  # wykonanie pętli dla każdego przypisania studentów
  for i in range(len(vec)):
    x=int(vec[i])

    # wybranie miejsca z pozostałych miejsc
    dorm=dorms[slots[x]]
    # wyświetlenie imienia studenta i nazwy przypisanego mu akademika
    print prefs[i][0],dorm
    # usunięcie wybranego miejsca
    del slots[x]

def dormcost(vec):
  cost=0
  # tworzenie listy miejsc
  slots=[0,0,1,1,2,2,3,3,4,4]

  # wykonanie pętli dla każdego studenta
  for i in range(len(vec)):
    x=int(vec[i])
    dorm=dorms[slots[x]]
    pref=prefs[i][1]
    # Pierwszy wybór kosztuje 0, a koszt drugiego wyboru to 1.
    if pref[0]==dorm: cost+=0
    elif pref[1]==dorm: cost+=1
    else: cost+=3
    # W przypadku braku na liście koszt wynosi 3.

    # usunięcie wybranego miejsca
    del slots[x]
    
  return cost

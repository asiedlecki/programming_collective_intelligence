from random import random,randint
import math

def wineprice(rating,age):
  peak_age=rating-50
  
  # obliczenie ceny na podstawie oceny
  price=rating/2
  if age>peak_age:
    # Po osiągnięciu optymalnego wieku w ciągu pięciu lat wino traci na jakości.
    price=price*(5-(age-peak_age)/2)
  else:
    # pięciokrotne zwiększenie początkowej ceny w momencie
    # osiągnięcia przez wino optymalnego wieku
    price=price*(5*((age+1)/peak_age))
  if price<0: price=0
  return price


def wineset1():
  rows=[]
  for i in range(300):
    # określanie losowego wieku i oceny
    rating=random()*50+50
    age=random()*50

    # uzyskanie ceny referencyjnej
    price=wineprice(rating,age)
    
    # zwiększenie stopnia trudności przewidywania ceny
    price*=(random()*0.2+0.9)

    # dodanie do zbioru danych
    rows.append({'input':(rating,age),
                 'result':price})
  return rows

def euclidean(v1,v2):
  d=0.0
  for i in range(len(v1)):
    d+=(v1[i]-v2[i])**2
  return math.sqrt(d)


def getdistances(data,vec1):
  distancelist=[]
  
  # wykonanie pętli dla każdego elementu w zbiorze danych
  for i in range(len(data)):
    vec2=data[i]['input']
    
    # dodanie odległości i indeksu
    distancelist.append((euclidean(vec1,vec2),i))
  
  # sortowanie według odległości
  distancelist.sort()
  return distancelist

def knnestimate(data,vec1,k=5):
  # uzyskanie posortowanych odległości
  dlist=getdistances(data,vec1)
  avg=0.0
  
  # uzyskanie średniej pierwszych k wyników
  for i in range(k):
    idx=dlist[i][1]
    avg+=data[idx]['result']
  avg=avg/k
  return avg

def inverseweight(dist,num=1.0,const=0.1):
  return num/(dist+const)

def subtractweight(dist,const=1.0):
  if dist>const: 
    return 0
  else: 
    return const-dist

def gaussian(dist,sigma=5.0):
  return math.e**(-dist**2/(2*sigma**2))

def weightedknn(data,vec1,k=5,weightf=gaussian):
  # uzyskanie odległości
  dlist=getdistances(data,vec1)
  avg=0.0
  totalweight=0.0
  
  # uzyskanie średniej ważonej
  for i in range(k):
    dist=dlist[i][0]
    idx=dlist[i][1]
    weight=weightf(dist)
    avg+=weight*data[idx]['result']
    totalweight+=weight
  if totalweight==0: return 0
  avg=avg/totalweight
  return avg

def dividedata(data,test=0.05):
  trainset=[]
  testset=[]
  for row in data:
    if random()<test:
      testset.append(row)
    else:
      trainset.append(row)
  return trainset,testset

def testalgorithm(algf,trainset,testset):
  error=0.0
  for row in testset:
    guess=algf(trainset,row['input'])
    error+=(row['result']-guess)**2
    #print row['result'],guess
  #print error/len(testset)
  return error/len(testset)

def crossvalidate(algf,data,trials=100,test=0.1):
  error=0.0
  for i in range(trials):
    trainset,testset=dividedata(data,test)
    error+=testalgorithm(algf,trainset,testset)
  return error/trials

def wineset2():
  rows=[]
  for i in range(300):
    rating=random()*50+50
    age=random()*50
    aisle=float(randint(1,20))
    bottlesize=[375.0,750.0,1500.0][randint(0,2)]
    price=wineprice(rating,age)
    price*=(bottlesize/750)
    price*=(random()*0.2+0.9)
    rows.append({'input':(rating,age,aisle,bottlesize),
                 'result':price})
  return rows

def rescale(data,scale):
  scaleddata=[]
  for row in data:
    scaled=[scale[i]*row['input'][i] for i in range(len(scale))]
    scaleddata.append({'input':scaled,'result':row['result']})
  return scaleddata

def createcostfunction(algf,data):
  def costf(scale):
    sdata=rescale(data,scale)
    return crossvalidate(algf,sdata,trials=20)
  return costf

weightdomain=[(0,10)]*4

def wineset3():
  rows=wineset1()
  for row in rows:
    if random()<0.5:
      # Wino zostało kupione w dyskoncie
      row['result']*=0.6
  return rows

def probguess(data,vec1,low,high,k=5,weightf=gaussian):
  dlist=getdistances(data,vec1)
  nweight=0.0
  tweight=0.0
  
  for i in range(k):
    dist=dlist[i][0]
    idx=dlist[i][1]
    weight=weightf(dist)
    v=data[idx]['result']
    
    # Czy ten punkt znajduje się w zakresie?
    if v>=low and v<=high:
      nweight+=weight
    tweight+=weight
  if tweight==0: return 0
  
  # Prawdopodobieństwo jest ilorazem wag w zakresie
  # i wszystkich wag.
  return nweight/tweight

from pylab import *

def cumulativegraph(data,vec1,high,k=5,weightf=gaussian):
  t1=arange(0.0,high,0.1)
  cprob=array([probguess(data,vec1,0,v,k,weightf) for v in t1])
  plot(t1,cprob)
  show()


def probabilitygraph(data,vec1,high,k=5,weightf=gaussian,ss=5.0):
  # utworzenie zakresu cen
  t1=arange(0.0,high,0.1)
  
  # uzyskanie prawdopodobieństw dla całego zakresu
  probs=[probguess(data,vec1,v,v+0.1,k,weightf) for v in t1]
  
  # wygładzenie prawdopodobieństw przez dodanie funkcji gaussian użytej dla sąsiednich prawdopodobieństw
  smoothed=[]
  for i in range(len(probs)):
    sv=0.0
    for j in range(0,len(probs)):
      dist=abs(i-j)*0.1
      weight=gaussian(dist,sigma=ss)
      sv+=weight*probs[j]
    smoothed.append(sv)
  smoothed=array(smoothed)
    
  plot(t1,smoothed)
  show()

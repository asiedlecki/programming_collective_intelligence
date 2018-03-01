import math

people=['Cezary','August','Wanda','Wiktoria','Michał','Jan','Waldek','Maria']

links=[('August', 'Waldek'),
       ('Michał', 'Jan'),
       ('Maria', 'Michał'),
       ('Wiktoria', 'August'),
       ('Maria', 'Waldek'),
       ('Cezary', 'Michał'),
       ('Wanda', 'Jan'),
       ('Maria', 'August'),
       ('Waldek', 'August'),
       ('Jan', 'Cezary'),
       ('Wanda', 'August'),
       ('Maria', 'Jan')]


def crosscount(v):
  # przekształcenie listy liczb w słownik osób: (x,y)
  loc=dict([(people[i],(v[i*2],v[i*2+1])) for i in range(0,len(people))])
  total=0
  
  # wykonanie pętli dla każdej pary łączy
  for i in range(len(links)):
    for j in range(i+1,len(links)):

      # uzyskanie lokalizacji 
      (x1,y1),(x2,y2)=loc[links[i][0]],loc[links[i][1]]
      (x3,y3),(x4,y4)=loc[links[j][0]],loc[links[j][1]]
      
      den=(y4-y3)*(x2-x1)-(x4-x3)*(y2-y1)

      # den==0, jeśli linie są równoległe.
      if den==0: continue

      # W przeciwnym razie ua i ub to część linii,
      # gdzie się one krzyżują.
      ua=((x4-x3)*(y1-y3)-(y4-y3)*(x1-x3))/den
      ub=((x2-x1)*(y1-y3)-(y2-y1)*(x1-x3))/den
      
      # Jeśli część zawiera się w przedziale od 0 do 1 dla obu linii,
      # krzyżują się one ze sobą.
      if ua>0 and ua<1 and ub>0 and ub<1:
        total+=1
    for i in range(len(people)):
      for j in range(i+1,len(people)):
        # uzyskanie lokalizacji dwóch węzłów
        (x1,y1),(x2,y2)=loc[people[i]],loc[people[j]]

        # określanie odległości między węzłami
        dist=math.sqrt(math.pow(x1-x2,2)+math.pow(y1-y2,2))
        # „karanie” wszystkich węzłów oddalonych od siebie o mniej niż 50 px
        if dist<50:
          total+=(1.0-(dist/50.0))
        
  return total
from PIL import Image,ImageDraw

def drawnetwork(sol):
  # tworzenie obrazu
  img=Image.new('RGB',(400,400),(255,255,255))
  draw=ImageDraw.Draw(img)

  # tworzenie słownika lokalizacji
  pos=dict([(people[i],(sol[i*2],sol[i*2+1])) for i in range(0,len(people))])

  for (a,b) in links:
    draw.line((pos[a],pos[b]),fill=(255,0,0))

  for n,p in pos.items():
    draw.text(p,n,(0,0,0))

  img.show()


domain=[(10,370)]*(len(people)*2)
from math import sqrt

# słownik krytyków filmowych i ich ocen niewielkiego zestawu filmów
critics = {'Lisa Rose': {'Kobieta w błękitnej wodzie': 2.5, 'Węże w samolocie': 3.5, 'Całe szczęście': 3.0,
                         'Superman: Powrót': 3.5, 'Ja, ty i on': 2.5, 'Nocny słuchacz': 3.0},
           'Gene Seymour': {'Kobieta w błękitnej wodzie': 3.0, 'Węże w samolocie': 3.5, 'Całe szczęście': 1.5,
                         'Superman: Powrót': 5.0, 'Ja, ty i on': 3.5, 'Nocny słuchacz': 3.0},
           'Michael Phillips': {'Kobieta w błękitnej wodzie': 2.5, 'Węże w samolocie': 3.0,
                         'Superman: Powrót': 3.5, 'Nocny słuchacz': 4.0},
           'Claudia Puig': {'Węże w samolocie': 3.5, 'Całe szczęście': 3.0,
                         'Superman: Powrót': 4.0, 'Ja, ty i on': 2.5, 'Nocny słuchacz': 4.5},
           'Mick LaSalle': {'Kobieta w błękitnej wodzie': 3.0, 'Węże w samolocie': 4.0, 'Całe szczęście': 2.0,
                         'Superman: Powrót': 3.0, 'Ja, ty i on': 2.0, 'Nocny słuchacz': 3.0},
           'Jack Matthews': {'Kobieta w błękitnej wodzie': 3.0, 'Węże w samolocie': 4.0,
                         'Superman: Powrót': 5.0, 'Ja, ty i on': 3.5, 'Nocny słuchacz': 3.0},
           'Toby': {'Węże w samolocie': 4.5, 'Superman: Powrót': 4.0, 'Ja, ty i on': 1.0}
            }

# zwracanie miary podobieństwa opartej na odległości euklidesowej dla pozycji person1 i person2
def sim_distance(prefs, person1, person2):
    # pobieranie listy wspólnych pozycji
    si={}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item]=1
    # w przypadku braku wspólnych ocen zostanie zwrócona wartość 0
    if len(si) == 0: return 0
    # sumowanie kwadratów wszystkich różnic
    sum_of_squares = sum([pow(prefs[person1][item]-prefs[person2][item], 2)
                          for item in prefs[person1] if item in prefs[person2]])
    return 1/(1+sum_of_squares) # odwracamy by większa cyfra oznaczała większe podobieństwo (1 - identyczne)
    # w mianowniku dodano 1, by uniknąć dzielenia przez zero

# zwracanie miary podobieństwa opartej na współczynniku korelacji Pearsona
def sim_pearson(prefs, person1, person2):
    # pobieranie listy wspólnych pozycji
    si={}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item]=1
    # znalezienie liczby elementow
    n = len(si)
    # w przypadku braku wspólnych ocen zostanie zwrócona wartość 0
    if len(si) == 0: return 0
    # sumowanie wszystkich preferencji
    sum1 = sum([prefs[person1][item] for item in si])
    sum2 = sum([prefs[person2][item] for item in si])
    # sumowanie potęg
    sum1Sq = sum([pow(prefs[person1][item], 2) for item in si])
    sum2Sq = sum([pow(prefs[person2][item], 2) for item in si])
    #sumowanie iloczynow
    pSum = sum([prefs[person1][item] * prefs[person2][item] for item in si])

    #obliczanie miary korelacji Pearsona
    num = pSum-(sum1*sum2/n)
    den = sqrt((sum1Sq-pow(sum1, 2)/n)*(sum2Sq-pow(sum2, 2)/n))
    if den == 0: return 0
    r = num / den
    return r

# Zwraca najlepsze dopasowania dla osoby ze slownika prefs
# liczba wynikow i funkcja podobienstwa to opcjonalne parametry
def topMatches(prefs, person, n=5, similarity=sim_pearson):
    scores=[(similarity(prefs, person, other), other)
            for other in prefs if other != person]
    # sortowanie listy tak, aby najwyzsze oceny znalazly sie na samej gorze
    scores.sort()
    scores.reverse()
    return scores [0:n]

# Uzyskiwanie rekomendacji dla osoby przy użyciu średniej ważonej
# rankingów wszystkich innych użytkowników
def getRecommendations(prefs, person, similarity = sim_pearson):
    totals = {}
    simSums = {}
    for other in prefs:
        # zapobieganie porównaniu mnie z samym sobą
        if other == person: continue
        sim = similarity(prefs, person, other)

        # ignorowanie ocen o wartości zerwoej lub niższej
        if sim <= 0: continue
        for item in prefs[other]:

            # Oceniane są tylko te filmy, których jeszcze nie widziałem
            if item not in prefs[person] or prefs[person][item] == 0:
                # miara podobieństwa * ocena filmu
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim
                # suma miar podobieństwa
                simSums.setdefault(item, 0)
                simSums[item] += sim

        # tworzenie listy znormalizowanej
        rankings = [(total/simSums[item], item) for item, total in totals.items()]

        # zwrócenie posortowanej listy
        rankings.sort()
        rankings.reverse()
        return rankings

# Funkcja transformuje listę ludzi z obejrzanymi przez nich filmami do listy filmów z przypisanymi do nich ludźmi
# którzy je ocenili oraz ich ocenami
def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})

            # zamiana miejscami pozycji i osoby
            result[item][person] = prefs[person][item]
    return result


# funkcja budująca pełny zbiór danych podobnych pozycji
def calculateSimilarItems(prefs, n=10):
    # tworzenie słownika pozycji prezentującego jakie inne pozycje są najbardziej podobne
    result = {}

    # odwrócenie macierzy preferencji, aby dotyczyła pozycji
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        # aktualizacje statusu dla dużych zbiorów danych
        c += 1
        if c % 100 == 0: print('{0} / {1}'.format(c, len(itemPrefs))) # printowanie postępu pętli
        # znajdowanie pozycji najbardziej podobnych do danej pozycji
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result

def getRecommendedItems(prefs, itemMatch, user):
    userRatings = prefs[user]
    scores = {}
    totalSim = {}

    # przetwarzanie w pętli pozycji ocenionych przez danego użytkownika
    for (item, rating) in userRatings.items():

        # przetwarzanie w pętli pozycji podobnych do danej pozycji
        for (similarity, item2) in itemMatch[item]:

            # Nastąpi zignorowanie, jeśli dany użytkownik ocenił już tę pozycję
            if item2 in userRatings: continue

            # suma ważona ocen pomnożona przez miarę podobieństwa
            scores.setdefault(item2, 0)
            scores[item2] += similarity*rating

            # suma wszystkich miar podobieństwa
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity

    # dzielenie każdej sumarycznej miary przez sumaryczną ważoną w celu uzyskania średniej
    rankings = [(score/totalSim[item], item) for item,score in scores.items()]

    #zwracanie rankingów w kolejności od najwyższych do najniższych
    rankings.sort()
    rankings.reverse()
    return rankings


# załadowanie zbioru MovieLens do pamięci operacyjnej
def loadMovieLens(path):

    # pobieranie tytułów filmów
    movies = {}
    for line in open(path + '/u.item'):
        (id, title) = line.split('|')[0:2]
        movies[id] = title

    # ładowanie danych
    prefs = {}
    for line in open(path + '/u.data'):
        (user_id, movie_id, rating, ts) = line.split('\t')
        prefs.setdefault(user_id, {})
        prefs[user_id][movies[movie_id]] = float(rating)
    return prefs
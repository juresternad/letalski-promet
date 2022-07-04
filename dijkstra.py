slovar_letalisc = {
    "Madrid Barajas Airport (MAD)": 0,
    "Barcelona Airport (BCN)": 1,
    "Rome Fiumicino Airport (FCO)": 2,
    "Zurich Airport (ZRH)": 3,
    "Athens Airport (ATH)": 4,
    "Munich International Airport (MUC)": 5,
    "Amsterdam Airport (AMS)": 6,
    "Frankfurt International Airport (FRA)": 7,
    "London Heathrow Airport (LHR)": 8,
    "Paris Charles de Gaulle Airport (CDG)": 9,
}

import heapq
C = 100000

# lahko dodas omejjitev skupnega casa potovanja, podobno kot pri ceni 

def dijkstraish(G, s, t): # upostevaj tudi cas kot sekundarni parameter
    seznam_cen = [float('infinity')]*(len(G))
    sez_predhodnikov = [None]*(len(G))
    # cas_letenja, skupni_cas_potovanja = [0]*(len(G)), [0]*(len(G))
    seznam_cen[s] = 0
    sez_predhodnikov[s] = s
    pq = [(0, 0, 0, s)]
    while pq:
        cur_cena, cur_t1, cur_t2, cur_node = heapq.heappop(pq)
        # check neighbours
        for (c, t1, t2, u) in G[cur_node]:
            c += cur_cena
            if c < seznam_cen[u] and cur_t2 < t1 and c <= C:
                seznam_cen[u] = c
                sez_predhodnikov[u] = cur_node
                # cas_letenja[u] += cur_t2 - cur_t1
                # skupni_cas_potovanja[u] += t1 - cur_t1
                heapq.heappush(pq, (c, t1, t2, u)) # order in tuple is not random
    return seznam_cen, sez_predhodnikov # , cas_letenja, skupni_cas_potovanja

def pot(sez_predhodnikov, s, t):
  pass
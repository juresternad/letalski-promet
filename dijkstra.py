
# cur.execute('select * from let where datum_odhoda > %s AND datum_odhoda < %s;', ())
# leti = cur.fetchall()

# slovar = {"ime letalisca": 0, ...}
# G = [[None]] * len(slovar) # seznam sosednosti
# for let in leti:
#   stevilka_leta = let[0]
#   vzletno_letalisce= let[0]
#   pristajalno_letalisce= let[0]
#   datum_odhoda= let[0]
#   datum_prihoda= let[0]
#   ura_odhoda= let[0]
#   ura_prihoda= let[0]
#   letalo_id= let[0]
#   ekipa= let[0]
#   cena= let[0]
#   G[slovar[vzletno_letalisce]].append(slovar[pristajalno_letalisce], datum_odhoda, datum_prihoda, ura_odhoda, ura_prihoda, cena)
#   G[slovar[vzletno_letalisce]].append(slovar[pristajalno_letalisce], cena)

# dijkstra glede na ceno a pri tem pazi da preveris cas (nek dodaten pogoj)
import heapq
C = 100000

def dijkstraish(G, s, t): # upostevaj tudi cas kot sekundarni parameter
    seznam_cen = [float('infinity')]*(len(G)+1)
    sez_predhodnikov = [None]*(len(G)+1)
    seznam_cen[s] = 0
    sez_predhodnikov[s] = s
    pq = [(0, s)]
    while pq:
        # current distance, cost, height, node
        cur_cena, cur_node = heapq.heappop(pq)
        # check neighbours
        for (c, u) in G[cur_node]:
            c += cur_cena
            if c < seznam_cen[u] and c <= C:
                seznam_cen[u] = c
                sez_predhodnikov[u] = cur_node
                heapq.heappush(pq, (c, u)) # order in tuple is not random
    return(seznam_cen[t], sez_predhodnikov)

def pot(sez_predhodnikov, s, t):
  pass
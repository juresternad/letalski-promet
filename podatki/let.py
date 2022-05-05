import random

sez_letov = []
sez_vzletnih_letalisc = ["London Heathrow Airport (LHR)", "Paris Charles de Gaulle Airport (CDG)", "Amsterdam Airport (AMS)", "Rome Fiumicino Airport (FCO)", "Madrid Barajas Airport (MAD)", "Munich International Airport (MUC)", "Barcelona Airport (BCN)", "Frankfurt International Airport (FRA)", "Athens Airport (ATH)", "Zurich Airport (ZRH)"]
print(len(sez_vzletnih_letalisc))
for i in range(10):
    stevilka_leta = i
    vzletno_letalisce = sez_vzletnih_letalisc[i]
    pristajalno_letalisce = None
    ekipa = i
    cas_prihoda = "2022-06-14 hh:mm:ss"
    cas_odhoda = "2022-06-14 hh:mm:ss"
    letalo = i
    sez_letov.append(f"insert into let (stevilka_leta, vzletno_letalisce, pristajalno_letalisce, cas_odhoda, cas_prihoda letalo, ekipa) values ({stevilka_leta}, {vzletno_letalisce}, {pristajalno_letalisce}, {cas_odhoda}, {cas_prihoda}, {letalo}, {ekipa})")

for i in sez_letov:
    print(i)
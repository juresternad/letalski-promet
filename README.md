# letalski-promet

[![bottle.py](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/juresternad/letalski-promet/main?urlpath=proxy/8080/) Aplikacija `bottle.py`



Aplikacija uporabnikom omogoča nakup letalskih kart. Na vstopni strani si uporabnik izbere željen kraj in čas odhoda ter prihoda. Pod izbirnim poljem se prav tako nahajajo last minute leti. 

Trenutno je postavljenih 20 možnih povezav (10 v vsako smer), ki so označene na spodnjem zemljevidu. Zaenkrat je mogoče izbirati le med direktnimi leti, v nadaljevanju razvoja aplikacije pa je v načrtu vpeljati tudi algoritem za iskanje najcenješe in najkrajše poti (npr. Dijkstra). Ta bo uporabniku že sam predlagal najhitrejše ter najcenejše možno prestopanje med posameznimi letališči.

<img src="slike/slika_leti.jpg">


Posamezen let nosi več podatkov: kateri tip letala uporablja, katera družba let izvaja, koliko sedežev je na letalu...  


<img src="./er_diagram.svg">

import psycopg2
import psycopg2.extensions
import psycopg2.extras
from bottleext import *
import os
import hashlib
import auth

# se znebimo problemov s šumniki
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

baza_datoteka = 'letalski_promet.db'
static_dir = "./static"

SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
ROOT = os.environ.get('BOTTLE_ROOT', '/')
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)


# odkomentiraj, če želiš sporočila o napakah TODO
debug(True)

####################################################


@get('/')  # landing page
def index():
    # TODO pogruntaj napako in mogoce dodaj try catch
    cur.execute(
        # TODO dodaj omejitev na top 20
        "SELECT (vzletno_letalisce, pristajalno_letalisce, cas_odhoda, cas_prihoda, stevilka_leta) FROM let;")
    leti = cur.fetchall()
    # grdo sej vem :()
    # print(leti[0][0].split(','))
    nleti = []
    for let in leti:
        let = let[0].split(',')
        vzletno = let[0][2:-1]
        pristajalno = let[1][1:-1]
        cas_odhoda = let[2]
        cas_prihoda = let[3][:-1]
        stevilka_leta = int(let[4][:-1]) # TODO mogoce se da lepse
        nleti.append([vzletno, pristajalno, cas_odhoda, cas_prihoda, stevilka_leta])
    return template('index.html', leti=nleti) # TODO ce si prijavljen naj desno zgoraj pise username in ne prijava in registracija


@post('/leti/')  # poizvedba za let
def let():
    iz = request.forms.iz
    do = request.forms.do
    datum_odhoda = request.forms.datum_odhoda
    datum_vrnitve = request.forms.datum_vrnitve
    cur.execute("SELECT * FROM let WHERE vzletno_letalisce = %s AND pristajalno_letalisce = %s AND cas_prihoda = %s AND cas_odhoda = %s;",
                (iz, do, datum_odhoda, datum_vrnitve))
    ustrezni_leti = cur.fetchall()
    if ustrezni_leti == []:
        return '<h2>Ni ustreznih letov!</h2>'
    else:
        return template('ustrezni_leti.html', ustrezni_leti=ustrezni_leti)



# TODO stevilo kart
@get('/kupi/<id_leta>')
def nakup_karte(id_leta):
    try:
        cur.execute("SELECT * FROM let WHERE stevilka_leta = %s;", (id_leta, ))
        let = cur.fetchall()[0][:5]
        return template('nakup_karte.html', let=let)
    except:
        return "Izbrani let ni na voljo!"

@post('/kupi/<id_leta>')
def kupi_karto(id_leta):
    # return f"kupili ste {id_leta}"
    username = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    if username is not None:
      try:
        # TODO stevilka_narocila mora biti auto generirana (to naredis v SQL)
        # TODO SELECT ime from uporabnik where uporabnisko_ime=username
        cur.execute("insert into karta (stevilka_narocila, razred, ime_potnika, cena, stevilka_sedeza, stevilka_leta) values (%s,%s,%s,%s,%s,%s);", 
        (5, "economy", username, 100, "3", id_leta))
        conn.commit()
        return template('uspesen_nakup.html', id_leta=id_leta)
      except:
        return "Žal nakup karte ni bil uspešen!"
    else:
        redirect(url('/prijava'))



############################################
### Registracija, prijava
############################################
def nastaviSporocilo(sporocilo=None): # TODO pri prijavi ne izpisuje sporocila
    # global napakaSporocilo
    staro = request.get_cookie("sporocilo", secret=skrivnost)
    if sporocilo is None:
        response.delete_cookie('sporocilo')
    else:
        response.set_cookie('sporocilo', sporocilo, path="/", secret=skrivnost)
    return staro


skrivnost = "banana"


def hashGesla(s):
    m = hashlib.sha256()
    m.update(s.encode("utf-8"))
    return m.hexdigest()


@get('/registracija')
def registracija_get():
    napaka = nastaviSporocilo()
    return template('registracija.html', napaka=napaka)


@post('/registracija')
def registracija_post():
    emso = request.forms.emso
    ime = request.forms.ime
    priimek = request.forms.priimek
    email = request.forms.email
    uporabnisko_ime = request.forms.username
    geslo = request.forms.password
    geslo2 = request.forms.password2
    if geslo != geslo2:
        nastaviSporocilo('Gesli se ne ujemata.')
        redirect('/registracija')
        return
    if len(geslo) < 4:
        nastaviSporocilo('Geslo mora imeti vsaj 4 znake.')
        redirect('/registracija')
        return
    if emso is None or uporabnisko_ime is None or geslo is None or geslo2 is None:
        nastaviSporocilo('Registracija ni možna')
        redirect('/registracija')
        return
    cur = conn.cursor()
    uporabnik = None
    try:
        uporabnik = cur.execute(
            "SELECT * FROM uporabnik WHERE emso = %s;", (emso, ))
    except:
        uporabnik = None
    if uporabnik is not None:
        nastaviSporocilo('Registracija ni možna')
        redirect('/registracija')
        return
    try:
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM uporabnik WHERE uporabnisko_ime = %s', (uporabnisko_ime, ))
        uporabnik = cur.fetchone()
    except:
        uporabnik = None
    if uporabnik is not None:
        nastaviSporocilo('Uporabnisko ime že obstaja!')
        redirect(url('/registracija'))
        return
    zgostitev = hashGesla(geslo)
    cur.execute('INSERT INTO uporabnik (emso, ime, priimek, email, uporabnisko_ime, geslo) VALUES (%s,%s,%s,%s,%s,%s);',
                (emso, ime, priimek, email, uporabnisko_ime, zgostitev))
    conn.commit()
    response.set_cookie('uporabnisko_ime', uporabnisko_ime, secret=skrivnost)
    redirect(url('/prijava'))


@get('/prijava')
def prijava_get():
    napaka = nastaviSporocilo()
    return template('prijava.html', napaka=napaka)


@post('/prijava')
def prijava_post():
    uporabnisko_ime = request.forms.username
    geslo = request.forms.password
    if uporabnisko_ime is None or geslo is None:
        nastaviSporocilo('Uporabniško ime in geslo morata biti neprazna')
        redirect('/prijava')
        return
    cur = conn.cursor()
    potnik_geslo = None
    organizator_geslo = None
    if geslo == '1111':
        redirect(url('/dodaj_organizatorja'))
    try:
        cur.execute(
            "SELECT geslo FROM organizator_letov WHERE uporabnisko_ime=%s;", (uporabnisko_ime, ))
        organizator_geslo = cur.fetchone()
        organizator_geslo = organizator_geslo[0]
    except:
        organizator_geslo = None

    try:
        cur.execute(
            "SELECT geslo FROM uporabnik WHERE uporabnisko_ime=%s;", (uporabnisko_ime, ))
        potnik_geslo = cur.fetchone()
        potnik_geslo = potnik_geslo[0]
    except:
        potnik_geslo = None

    curr = conn.cursor() # TODO delete this because it is not used
    if potnik_geslo is None and organizator_geslo is None:
        nastaviSporocilo('Uporabniško geslo ali ime nista ustrezni')
        redirect(url('/prijava'))
        return
    if hashGesla(geslo) != potnik_geslo and hashGesla(geslo) != organizator_geslo:
        nastaviSporocilo('Uporabniško geslo ali ime nista ustrezni')
        redirect(url('/prijava'))
        return

    response.set_cookie('uporabnisko_ime', uporabnisko_ime, secret=skrivnost)
    if potnik_geslo is None:
        redirect(url('/profil_organizatorja'))

    if organizator_geslo is None:
        redirect(url('/profil_uporabnika'))


@get('/odjava')
def odjava_get():
    response.delete_cookie('uporabnisko_ime')
    redirect('/prijava')

############################################
### Začetne strani
############################################

@get('/profil_uporabnika')
def profil_uporabnika():
    napaka = nastaviSporocilo()
    username = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    cur.execute(
        "SELECT emso, ime, priimek, uporabnisko_ime FROM uporabnik WHERE uporabnisko_ime = %s;", (username, ))
    uporabnik = cur.fetchall()
    cur.execute(
        "SELECT * FROM karta WHERE ime_potnika = %s;", (username, ))
    kupljene_karte = cur.fetchall()
    leti = []
    for karta in kupljene_karte:
        stevilka_leta = karta[0]
        cur.execute(
        "SELECT stevilka_leta, vzletno_letalisce, pristajalno_letalisce, cas_odhoda FROM let WHERE stevilka_leta = %s;", (stevilka_leta, ))
        leti.append(cur.fetchall()[0]) # pri karti je treba dodati cas nakupa karte in pri letu pa se uro
    return template('profil_uporabnika.html', uporabnik=uporabnik, leti=leti, napaka=napaka)

@get('/profil_organizatorja')
def profil_organizatorja():
    napaka = nastaviSporocilo()
    username = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    cur.execute(
        "SELECT emso, ime, priimek, uporabnisko_ime FROM organizator_letov WHERE uporabnisko_ime = %s;", (username, ))
    organizator_letov = cur.fetchall()
    print()
    return template('profil_organizatorja.html', organizator_letov=organizator_letov, napaka=napaka)

############################################
### Dodajanje organizatorja
############################################

@get('/dodaj_organizatorja')
def dodaj_organizatorja_get():
    napaka = nastaviSporocilo()
    return template('dodaj_organizatorja.html', napaka=napaka)


@post('/dodaj_organizatorja')
def dodaj_organizatorja_post():
    emso = request.forms.emso
    ime = request.forms.ime
    priimek = request.forms.priimek
    uporabnisko_ime = request.forms.username
    geslo = request.forms.password
    cur = conn.cursor()
    uporabnik = None
    try:
        uporabnik = cur.execute(
            "SELECT * FROM organizator_letov WHERE emso = %s;", (emso, ))
    except:
        uporabnik = None
    if uporabnik is not None:
        nastaviSporocilo('Dodajanje organizatorja ni možno')
        redirect('/dodaj_organizatorja')
        return
    try:
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM organizator_letov WHERE uporabnisko_ime = %s;', (uporabnisko_ime, ))
        uporabnik = cur.fetchone()
    except:
        uporabnik = None
    if uporabnik is not None:
        nastaviSporocilo('Uporabnisko ime že obstaja!')
        redirect(url('/dodaj_organizatorja'))
        return
    zgostitev = hashGesla(geslo)
    cur.execute("INSERT INTO organizator_letov (emso, ime, priimek, uporabnisko_ime, geslo) VALUES (%s, %s, %s, %s, %s);", (emso, ime, priimek, uporabnisko_ime, zgostitev))
    conn.commit()
    response.set_cookie('uporabnisko_ime', uporabnisko_ime, secret=skrivnost)
    redirect(url('/prijava'))
####################################################


# povezemo se z bazo
conn = psycopg2.connect(database=auth.db, user=auth.user,
                        password=auth.password, host=auth.host, port=DB_PORT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# zazenemo/povezemo se s streznikom
run(host='localhost', port=SERVER_PORT, reloader=True)


###################################################
@get('/leti/<od:text>/<do:text>/<datum_odhoda:int>/<datum_prihoda:int>/<razred:text>')
def ustrezni_leti(od, do, datum_odhoda, datum_prihoda, razred):
    
    # cur.execute("SELECT * FROM leti WHERE vzletno_letalisce = %s AND pristajalno_letalisce = %s AND cas_odhoda, cas_prihoda > %s ORDER BY znesek, id", [od, do, datum_odhoda, datum_prihoda, razred])
    cur.execute("SELECT (vzletno_letalisce, pristajalno_letalisce) FROM leti WHERE ...")
    # ustvarimo seznam 
    povezave = []
    for i in cur:
        povezave.append(i)
    
    vozlisca = []

    cur.execute("SELECT DISTINCT vzletno_letalisce FROM leti WHERE ...")
    for i in cur:
        vozlisca.append(i)

    bfs(od, do)
    return template('transakcije.html', x=x, transakcije=cur)

def dijkstraish(G, s, t, C, D, H):
    ds = [float('infinity')]*(n+1)
    hs = [float('infinity')]*(n+1)
    cs = [float('infinity')]*(n+1)
    ds[s] = 0
    hs[s] = 0
    cs[s] = 0
    pq = [(0, 0, 0, s)]
    while pq:
        # current distance, cost, height, node
        cur_d, cur_c, cur_h, cur_node = heapq.heappop(pq)
        # check neighbours
        for (h, d, c, s) in G[cur_node]:
            h = max(cur_h, h)
            d += cur_d
            c += cur_c
            if d < ds[s] and h <= H and d <= D and c <= C:
                hs[s] = h
                cs[s] = c
                ds[s] = d
                heapq.heappush(pq, (d, c, h, s)) # order in tuple is not random
            # Maybe there is lower cost with same distance!:
            elif d == ds[s] and c < cs[s] and h <= H and d <= D and c <= C:
                hs[s] = h
                cs[s] = c
                ds[s] = d
                heapq.heappush(pq, (d, c, h, s)) # order in tuple is not random
    return(hs[t], ds[t], cs[t])

import psycopg2
import psycopg2.extensions
import psycopg2.extras
from regex import P
from bottleext import *
import os
import hashlib
# import auth_g
import auth_public as auth_g

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

baza_datoteka = 'letalski_promet.db'
static_dir = "./static"

SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
ROOT = os.environ.get('BOTTLE_ROOT', '/')
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)


debug(True)

############################################
### index
############################################


@get('/')  
def index():
    uporabnik = aliUporabnik()
    organizator = aliOrganizator()
    admin = aliAdmin()
    leti = []
    return template('index.html', leti=leti, uporabnik=uporabnik, organizator=organizator, admin = admin)

@get("/views/images/<filepath:re:.*\.(jpg|png|gif|ico|svg)>")
def img(filepath):
    return static_file(filepath, root="views/images")

@route("/static/<filename:path>")
def static(filename):
    return static_file(filename, root=static_dir)
    
@get('/last_minute')  
def last_minute():
    uporabnik = aliUporabnik()
    organizator = aliOrganizator()
    admin = aliAdmin()
    leti = []
    try:
        cur.execute(
            "SELECT * FROM let WHERE  datum_odhoda < CURRENT_DATE + INTERVAL '3 day' ORDER BY datum_odhoda, ura_odhoda;")
        leti = cur.fetchall()
    except:
        return "Napaka!"
    return template('last_minute.html', leti=leti, uporabnik=uporabnik, organizator=organizator,admin = admin)

@get('/vroci')  
def vroci():
    uporabnik = aliUporabnik()
    organizator = aliOrganizator()
    admin = aliAdmin()
    leti = []
    try:
        cur.execute(
            "SELECT * FROM let WHERE CURRENT_DATE < datum_odhoda OR (CURRENT_DATE = datum_odhoda AND CURRENT_TIME < ura_odhoda) ORDER BY st_zasedenih_mest[1] DESC, datum_odhoda, ura_odhoda LIMIT 10;")
        leti = cur.fetchall()
    except:
        return "Napaka!"
    return template('vroci.html', leti=leti, uporabnik=uporabnik, organizator=organizator,admin = admin)


@get('/carterski')  
def carterski():
    uporabnik = aliUporabnik()
    organizator = aliOrganizator()
    admin = aliAdmin()
    leti = []
    try:
        cur.execute(
            "SELECT * FROM let WHERE CURRENT_DATE < datum_odhoda OR (CURRENT_DATE = datum_odhoda AND CURRENT_TIME < ura_odhoda) ORDER BY datum_odhoda, ura_odhoda;")
        leti = cur.fetchall()
    except:
        return "Napaka!"
    return template('carterski.html', leti=leti, uporabnik=uporabnik, organizator=organizator,admin = admin)



@post('/leti')  
def let():
    iz = request.forms.iz
    do = request.forms.do
    datum_odhoda = request.forms.datum_odhoda
    datum_vrnitve = request.forms.datum_vrnitve
    razred = request.forms.razred
    enosmeren = request.forms.enosmeren
    redirect(url('d', iz="-".join(iz.split()), do="-".join(do.split()), datum_odhoda=datum_odhoda,
             datum_prihoda=datum_vrnitve, razred=razred, enosmeren=enosmeren))
    

############################################
### Nakup karte
############################################

@get('/kupi/<id_leta>')
def nakup_karte(id_leta):
    try:
        cur.execute("SELECT * FROM let WHERE stevilka_leta = %s;", (id_leta, ))
        let = cur.fetchall()[0]
        return template('nakup_karte.html', let=let)
    except:
        return "Izbrani let ni na voljo!"

@post('/kupi/<id_leta>') 
def kupi_karto(id_leta):
    username = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    razred = request.forms.razred
    st_kart = int(request.forms.st_kart)
    if username is not None:
        for _ in range(st_kart):
            cur.execute("insert into karta (razred, uporabnisko_ime, stevilka_leta) values (%s,%s,%s);", 
            (razred, username, id_leta))
            conn.commit()
        cur.execute("SELECT * FROM let WHERE stevilka_leta = %s;", (id_leta, ))
        kup_karta = cur.fetchone()
        iz, do, datum, ura, st_zas_mest, st_pro_mest = kup_karta[1], kup_karta[2], kup_karta[3], kup_karta[5], kup_karta[10], kup_karta[11]
        if razred == "economy":
            i = 0
        elif razred == "business":
            i = 1
        else:
            i = 2
        prosto = st_pro_mest[i] - st_kart
        if prosto >= 0:
            st_zas_mest[i] += st_kart
            st_pro_mest[i] -= st_kart
            cur.execute("UPDATE let SET st_zasedenih_mest = %s, st_prostih_mest = %s WHERE stevilka_leta = %s;", (st_zas_mest, st_pro_mest, id_leta, ))
            return template('uspesen_nakup.html', iz=iz, do=do, datum=datum, ura=ura, st_kart=st_kart)
        return "Žal ni več prostih sedežev. Za izbrani razred je trenutno na voljo samo še {}.".format(st_pro_mest[i])
    else:
        redirect(url('/prijava'))



############################################
### Napaka, uporabnik, organizator, admin
############################################


skrivnost = "a46dba37408900668dc726215eada82d5f564b0b13dec05552d856e534bb62e4"

def nastaviSporocilo(sporocilo = None):
    staro = request.get_cookie("sporocilo", secret=skrivnost)
    if sporocilo is None:
        response.delete_cookie('sporocilo', path="/")
    else:
        response.set_cookie('sporocilo', sporocilo, secret=skrivnost, path="/")
    return staro 
    
def aliUporabnik(): 
    username = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    if username:
        cur = conn.cursor()
        uporabnik = None
        try: 
            cur.execute('SELECT * FROM uporabnik WHERE uporabnisko_ime = %s', (username, ))
            uporabnik = cur.fetchone()
        except:
            uporabnik = None
        if uporabnik: 
            return uporabnik
    

def aliOrganizator(): 
    username = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    if username:
        cur = conn.cursor()
        organizator = None
        try: 
            cur.execute('SELECT * FROM organizator_letov WHERE uporabnisko_ime = %s', (username, ))
            organizator = cur.fetchone()
        except:
            organizator = None
        if organizator: 
            return organizator
            
def aliAdmin(): 
    username = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    if username:
        cur = conn.cursor()
        admin = None
        try: 
            cur.execute('SELECT emso FROM uporabnik WHERE uporabnisko_ime = %s', (username, ))
            admin = cur.fetchone()
            if admin[0] == 1: 
                return admin
        except:
            admin = None
        
############################################
### Registracija, prijava, odjava, sprememba gesla
############################################

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
        redirect(url('/registracija'))
    if len(geslo) < 4:
        nastaviSporocilo('Geslo mora imeti vsaj 4 znake.')
        redirect(url('/registracija'))
    if emso is None or uporabnisko_ime is None or geslo is None or geslo2 is None:
        nastaviSporocilo('Vnesi vse podatke')
        redirect(url('/registracija'))

    cur = conn.cursor()
    uporabnik = None
    try:
        uporabnik = cur.execute(
            "SELECT * FROM uporabnik WHERE emso = %s;", (emso, ))
    except:
        uporabnik = None
    if uporabnik is not None:
        nastaviSporocilo('Uporabnik s tem emšom obstaja')
        redirect(url('/registracija'))
    try:
        cur = conn.cursor()
        uporabnik = cur.execute('SELECT * FROM uporabnik WHERE uporabnisko_ime = %s', (uporabnisko_ime, ))
    except:
        uporabnik = None
    if uporabnik is not None:
        nastaviSporocilo('Uporabnisko ime že obstaja!')
        redirect(url('/registracija'))

    zgostitev = hashGesla(geslo)
    cur.execute('INSERT INTO uporabnik (emso, ime, priimek, email, uporabnisko_ime, geslo) VALUES (%s,%s,%s,%s,%s,%s);',
                (emso, ime, priimek, email, uporabnisko_ime, zgostitev))
    conn.commit()
    response.set_cookie('uporabnisko_ime', uporabnisko_ime, secret=skrivnost)
    redirect(url('/'))


@get('/prijava')
def prijava_get():
    napaka = nastaviSporocilo()
    return template('prijava.html', napaka=napaka)


@post('/prijava')
def prijava_post():
    uporabnisko_ime = request.forms.username
    geslo = request.forms.password
    cur = conn.cursor()
    potnik_geslo = None
    organizator_geslo = None
    try:
        cur.execute(
            "SELECT geslo FROM uporabnik WHERE uporabnisko_ime=%s;", (uporabnisko_ime, ))
        potnik_geslo = cur.fetchone()
        potnik_geslo = potnik_geslo[0]
    except: 
        potnik_geslo = None
    try:
        cur.execute(
            "SELECT geslo FROM organizator_letov WHERE uporabnisko_ime=%s;", (uporabnisko_ime, ))
        organizator_geslo = cur.fetchone()
        organizator_geslo = organizator_geslo[0]
    except:
        organizator_geslo = None
    cur = conn.cursor()
    if potnik_geslo is None and organizator_geslo is None and geslo != potnik_geslo:
        nastaviSporocilo('Uporabnik ne obstaja')
        redirect(url('/prijava'))
        return
    elif hashGesla(geslo) != potnik_geslo and hashGesla(geslo) != organizator_geslo and geslo != potnik_geslo: 
        nastaviSporocilo('Uporabniško ime in geslo se ne ujemata')
        redirect(url('/prijava'))
        return
    response.set_cookie('uporabnisko_ime', uporabnisko_ime, secret=skrivnost)
    if geslo == potnik_geslo:
        response.set_cookie('uporabnisko_ime', uporabnisko_ime, secret=skrivnost)
        redirect(url('/'))
    elif potnik_geslo is None:
        redirect(url('/'))
    elif organizator_geslo is None:
        redirect(url('/'))



@get('/odjava')
def odjava_get():
    response.delete_cookie('uporabnisko_ime')
    redirect(url('index'))

@get('/sprememba_gesla')
def sprememba_gesla():
    napaka = nastaviSporocilo()
    uporabnik = aliUporabnik()
    organizator = aliOrganizator()
    admin = aliAdmin()
    return template('sprememba_gesla.html', napaka=napaka,uporabnik=uporabnik, organizator=organizator, admin = admin)

@post('/sprememba_gesla')
def sprememba_gesla_post():
    uporabnisko_ime = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    geslo1 = request.forms.geslo1
    geslo2 = request.forms.geslo2
    if geslo1 != geslo2:
        nastaviSporocilo('Gesli se ne ujemata') 
        redirect(url('/sprememba_gesla'))
        return
    if len(geslo1) < 4:
        nastaviSporocilo('Geslo mora imeti vsaj 4 znake.') 
        redirect(url('/sprememba_gesla'))
        return 
    cur = conn.cursor()
    if uporabnisko_ime:    
        uporabnik1 = None
        uporabnik2 = None
        try: 
            cur = conn.cursor()
            cur.execute("SELECT * FROM organizator_letov WHERE uporabnisko_ime = %s", (uporabnisko_ime, ))
            uporabnik1 = cur.fetchone()
        except:
            uporabnik1 = None
        try: 
            cur = conn.cursor()
            cur.execute("SELECT * FROM uporabnik WHERE uporabnisko_ime = %s", (uporabnisko_ime, ))
            uporabnik2 = cur.fetchone()            
        except:
            uporabnik2 = None    
        if uporabnik1: 
            zgostitev1 = hashGesla(geslo1)
            cur.execute("UPDATE organizator_letov SET geslo = %s WHERE  = %s", (zgostitev1 ,uporabnisko_ime))
            conn.commit()
            return redirect(url('/prijava'))
        if uporabnik2:
            zgostitev2 = hashGesla(geslo2)
            cur.execute("UPDATE uporabnik SET  geslo = %s WHERE uporabnisko_ime = %s", (zgostitev2 ,uporabnisko_ime))
            conn.commit()
            return redirect(url('/prijava'))
    nastaviSporocilo('Obvezna registracija') 
    redirect(url('/registracija'))

############################################
### Profili
############################################

@get('/profil_uporabnika')
def profil_uporabnika():
    admin = aliAdmin()
    organizator= aliOrganizator()
    napaka = nastaviSporocilo()
    username = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    cur.execute(
        "SELECT emso, ime, priimek, email, uporabnisko_ime FROM uporabnik WHERE uporabnisko_ime = %s;", (username, ))
    uporabnik2 = cur.fetchall()
    uporabnik = aliUporabnik()
    return template('profil_uporabnika.html', uporabnik2=uporabnik2,uporabnik=uporabnik, napaka=napaka,admin=admin, organizator = organizator)


@get('/kupljene_karte')
def kupljene_karte():
    napaka = nastaviSporocilo()
    username = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    uporabnik = aliUporabnik()
    admin = aliAdmin()
    organizator= aliOrganizator()
    if username is not None:
        cur.execute(
            "SELECT emso, ime, priimek, uporabnisko_ime FROM uporabnik WHERE uporabnisko_ime = %s;", (username, ))
        cur.execute(
            "SELECT * FROM karta WHERE uporabnisko_ime = %s;", (username, ))
        kupljene_karte = cur.fetchall()
        leti = []
        for karta in kupljene_karte:
            stevilka_leta = karta[4]
            cur.execute(
            "SELECT stevilka_leta, vzletno_letalisce, pristajalno_letalisce, datum_odhoda, ura_odhoda FROM let WHERE stevilka_leta = %s LIMIT 1;", (stevilka_leta, )) 
            leti.append(cur.fetchone())
        return template('kupljene_karte.html', uporabnik=uporabnik, leti=leti, napaka=napaka,admin=admin, organizator = organizator)
    else:
        redirect(url('/prijava'))

@get('/profil_organizatorja')
def profil_organizatorja():
    uporabnik = aliUporabnik()
    admin = aliAdmin()
    organizator= aliOrganizator()
    napaka = nastaviSporocilo()
    username = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    cur.execute(
        "SELECT emso, ime, priimek, uporabnisko_ime FROM organizator_letov WHERE uporabnisko_ime = %s;", (username, ))
    organizator_letov = cur.fetchall()
    return template('profil_organizatorja.html', organizator_letov=organizator_letov, napaka=napaka,uporabnik=uporabnik, admin=admin, organizator = organizator)



############################################
### Dodajanje organizatorja
############################################

@get('/dodaj_organizatorja')
def dodaj_organizatorja_get():
    uporabnik = aliUporabnik()
    admin = aliAdmin()
    if admin is None:
        return 
    organizator = aliOrganizator()
    napaka = nastaviSporocilo()
    return template('dodaj_organizatorja.html', napaka=napaka, uporabnik=uporabnik, admin=admin, organizator = organizator)


@post('/dodaj_organizatorja')
def dodaj_organizatorja_post():
    emso = request.forms.emso
    ime = request.forms.ime
    priimek = request.forms.priimek
    uporabnisko_ime = request.forms.username
    geslo = request.forms.password
    cur = conn.cursor()
    organizatorr = None
    try:
        organizatorr = cur.execute(
            "SELECT * FROM organizator_letov WHERE emso = %s;", (emso, ))
    except:
        organizatorr = None
    if organizatorr is not None:
        nastaviSporocilo('Dodajanje organizatorja ni možno')
        redirect(url('/dodaj_organizatorja'))
        return
    try:
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM organizator_letov WHERE uporabnisko_ime = %s;', (uporabnisko_ime, ))
        organizatorr = cur.fetchone()
    except:
        organizatorr = None
    try:
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM uporabnik WHERE uporabnisko_ime = %s;', (uporabnisko_ime, ))
        organizatorr = cur.fetchone()
    except:
        organizatorr = None
    if organizatorr is not None:
        nastaviSporocilo('Uporabnisko ime že obstaja!')
        redirect(url('/dodaj_organizatorja'))
        return
    zgostitev = hashGesla(geslo)
    cur.execute("INSERT INTO organizator_letov (emso, ime, priimek, uporabnisko_ime, geslo) VALUES (%s, %s, %s, %s, %s);", (emso, ime, priimek, uporabnisko_ime, zgostitev))
    conn.commit()
    redirect(url('/pregled_organizatorjev'))



############################################
### Dodajanje leta
############################################

@get('/dodaj_let')
def dodaj_let_get():
    organizator = aliOrganizator()
    uporabnik = aliUporabnik()
    admin = aliAdmin()
    if admin is None and organizator is None:
        return
    napaka = nastaviSporocilo()
    return template('dodaj_let.html', napaka=napaka, organizator=organizator, uporabnik = uporabnik,admin = admin)

@post('/dodaj_let')
def dodaj_let_post():
    vzletno_letalisce = request.forms.vzletno_letalisce
    pristajalno_letalisce = request.forms.pristajalno_letalisce
    datum_odhoda = request.forms.datum_odhoda
    datum_prihoda = request.forms.datum_prihoda
    ura_odhoda = request.forms.ura_odhoda
    ura_prihoda = request.forms.ura_prihoda
    letalo_id = request.forms.letalo_id
    ekipa = request.forms.ekipa
    cenae = int(request.forms.cenae)
    cenab = int(request.forms.cenab)
    cenaf = int(request.forms.cenaf)
    prostae = int(request.forms.prostae)
    prostab = int(request.forms.prostab)
    prostaf = int(request.forms.prostaf)
    cena = [cenae,cenab,cenaf]
    prosta = [prostae,prostab,prostaf]
    cur = conn.cursor()
    cur.execute("INSERT INTO let (vzletno_letalisce, pristajalno_letalisce, datum_odhoda, datum_prihoda, ura_odhoda, ura_prihoda, letalo_id, ekipa, cena, st_zasedenih_mest, st_prostih_mest) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (vzletno_letalisce, pristajalno_letalisce, datum_odhoda, datum_prihoda, ura_odhoda, ura_prihoda, letalo_id, ekipa, cena, [0,0,0], prosta  ))
    conn.commit()
    redirect(url('/'))
####################################################

############################################
### Optimalna pot - Dijkstra
############################################
from dijkstra import slovar_letalisc, dijkstraish, pot
from datetime import datetime

@get('/d/<iz>/<do>/<datum_odhoda>/<datum_prihoda>/<razred>/<enosmeren>')
def d(iz, do, datum_odhoda, datum_prihoda, razred=0, enosmeren=0):

    cur.execute("SELECT stevilka_leta, vzletno_letalisce, pristajalno_letalisce, datum_odhoda, datum_prihoda, ura_odhoda, ura_prihoda, cena FROM let WHERE datum_odhoda < %s:: date + INTERVAL '3 day' AND datum_odhoda >= %s:: date ;", (datum_odhoda, datum_odhoda))
    leti = cur.fetchall()
    G = [[] for _ in range(len(slovar_letalisc))] # seznam sosednosti
    for let in leti:
        stevilka_leta, vzletno_letalisce, pristajalno_letalisce, datum_odhoda, datum_prihoda, ura_odhoda, ura_prihoda, cene = let
        if vzletno_letalisce not in slovar_letalisc:
            continue
        d1 = datetime.combine(datum_odhoda, ura_odhoda)
        t1 = datetime.timestamp(d1)
        d2 = datetime.combine(datum_prihoda, ura_prihoda)
        t2 = datetime.timestamp(d2)
        G[slovar_letalisc[vzletno_letalisce]].append((cene[int(razred)], t1, t2, slovar_letalisc[pristajalno_letalisce], stevilka_leta))
    s, t = slovar_letalisc[" ".join(iz.split("-"))], slovar_letalisc[" ".join(do.split("-"))]
    cena_potovanja, pot = dijkstraish(G, s, t)
    pot_tja = []
    for st_leta in pot:
        cur.execute('SELECT vzletno_letalisce, pristajalno_letalisce, datum_odhoda, datum_prihoda, ura_odhoda, ura_prihoda, cena, stevilka_leta FROM let WHERE stevilka_leta = %s', (st_leta, ))
        pot_tja.append(cur.fetchone())

    cur.execute("SELECT stevilka_leta, vzletno_letalisce, pristajalno_letalisce, datum_odhoda, datum_prihoda, ura_odhoda, ura_prihoda, cena FROM let WHERE datum_odhoda < %s:: date + INTERVAL '3 day' AND datum_odhoda >= %s:: date ;", (datum_prihoda, datum_prihoda ))
    leti2 = cur.fetchall()
    M = [[] for _ in range(len(slovar_letalisc))] # seznam sosednosti
    for let2 in leti2 :
        stevilka_leta2, vzletno_letalisce2, pristajalno_letalisce2, datum_odhoda2, datum_prihoda2, ura_odhoda2, ura_prihoda2, cene2 = let2
        if vzletno_letalisce2 not in slovar_letalisc:
            continue
        d12 = datetime.combine(datum_odhoda2, ura_odhoda2)
        t12 = datetime.timestamp(d12)
        d22 = datetime.combine(datum_prihoda2, ura_prihoda2)
        t22 = datetime.timestamp(d22)
        M[slovar_letalisc[vzletno_letalisce2]].append((cene2[int(razred)], t12, t22, slovar_letalisc[pristajalno_letalisce2], stevilka_leta2))
    s2, t2 = slovar_letalisc[" ".join(do.split("-"))], slovar_letalisc[" ".join(iz.split("-"))]
    cena_potovanja_nazaj, pot2 = dijkstraish(M, s2, t2)
    pot_nazaj = []
    for st_leta2 in pot2:
        cur.execute('SELECT vzletno_letalisce, pristajalno_letalisce, datum_odhoda, datum_prihoda, ura_odhoda, ura_prihoda, cena, stevilka_leta FROM let WHERE stevilka_leta = %s', (st_leta2, ))
        pot_nazaj.append(cur.fetchone())
    return template('dijkstra_let.html', cena_potovanja=cena_potovanja,cena_potovanja_nazaj=cena_potovanja_nazaj, pot_tja=pot_tja,pot_nazaj=pot_nazaj,razred=razred, enosmeren = enosmeren)

    



############################################
### Urejanje letov
############################################
@get('/pregled_letov')  
def pregled_letov():
    organizator = aliOrganizator()
    uporabnik = aliUporabnik()
    admin = aliAdmin()
    if admin is None and organizator is None:
        return
    leti = []
    try:
        cur.execute(
            "SELECT * FROM let")
        leti = cur.fetchall()
    except:
        return "Napaka!"
    return template('pregled_letov.html', leti=leti, uporabnik=uporabnik, organizator=organizator,admin = admin)



@get('/uredi/<id_leta>')
def uredi(id_leta):
    uporabnik = aliUporabnik()
    organizator = aliOrganizator()
    admin = aliAdmin()
    if admin is None and organizator is None:
        return
    try:
        cur.execute("SELECT * FROM let WHERE stevilka_leta = %s;", (id_leta, ))
        let = cur.fetchall()[0]
        return template('uredi.html', let=let,uporabnik = uporabnik, organizator = organizator, admin = admin)
    except:
        return "Izbrani let ni na voljo!"

@post('/uredi/<id_leta>') 
def uredi_post(id_leta):
    organizator = aliOrganizator()
    uporabnik = aliUporabnik()
    admin = aliAdmin()
    if admin is None and organizator is None:
        return
    leti = []
    try:
        vzletno_letalisce = request.forms.vzletno_letalisce
        pristajalno_letalisce = request.forms.pristajalno_letalisce
        datum_odhoda = request.forms.datum_odhoda
        datum_prihoda = request.forms.datum_prihoda
        ura_odhoda = request.forms.ura_odhoda
        ura_prihoda = request.forms.ura_prihoda
        letalo_id = request.forms.letalo_id
        ekipa = request.forms.ekipa
        cenae = int(request.forms.cenae)
        cenab = int(request.forms.cenab)
        cenaf = int(request.forms.cenaf)
        prostae = int(request.forms.prostae)
        prostab = int(request.forms.prostab)
        prostaf = int(request.forms.prostaf)
        cena = [cenae,cenab,cenaf]
        prosta = [prostae,prostab,prostaf]
        cur.execute("UPDATE let SET vzletno_letalisce = %s, pristajalno_letalisce = %s, datum_odhoda = %s, datum_prihoda = %s, ura_odhoda = %s, ura_prihoda = %s, letalo_id = %s, ekipa = %s, cena = %s, st_zasedenih_mest = %s, st_prostih_mest = %s WHERE stevilka_leta = %s;", (vzletno_letalisce, pristajalno_letalisce, datum_odhoda, datum_prihoda, ura_odhoda, ura_prihoda, letalo_id, ekipa, cena, [0,0,0], prosta,  id_leta ))
        conn.commit()
        leti = []
        cur.execute(
                "SELECT * FROM let")
        leti = cur.fetchall()
        return template('pregled_letov.html', leti = leti, uporabnik = uporabnik, organizator = organizator, admin = admin)
    except:
        return "Izbrani let ni na voljo!"


@get('/odstrani/<id_leta>')
def odstrani(id_leta):
    organizator = aliOrganizator()
    admin = aliAdmin()
    uporabnik = aliUporabnik()
    if admin is None and organizator is None:
        return
    leti = []

    cur.execute("DELETE FROM let WHERE stevilka_leta = %s;", (id_leta, ))
    conn.commit()
    cur.execute(
        "SELECT * FROM let")
    leti = cur.fetchall()
    return template('pregled_letov.html', leti = leti, organizator = organizator, admin = admin, uporabnik = uporabnik)

############################################
### Urejanje uporabnikov
############################################


@get('/pregled_uporabnikov')  
def pregled_uporabnikov():
    organizator = aliOrganizator()
    uporabnik = aliUporabnik()
    admin = aliAdmin()
    if admin is None:
        return
    uporabniki = []
    try:
        cur.execute(
            "SELECT * FROM uporabnik")
        uporabniki = cur.fetchall()
        return template('pregled_uporabnikov.html', uporabniki=uporabniki, uporabnik=uporabnik,admin = admin, organizator = organizator)
    except:
        return "Napaka!"


@get('/uredi_uporabnika/<emso>') 
def uredi_uporabnika(emso):
    uporabnik = aliUporabnik()
    admin = aliAdmin()
    organizator = aliOrganizator()
    if admin is None:
        return
    cur.execute("SELECT * FROM uporabnik WHERE emso = %s;", (emso, ))
    uporabnik2 = cur.fetchall()[0]
    return template('uredi_uporabnika.html', uporabnik = uporabnik, admin = admin, organizator = organizator, uporabnik2 = uporabnik2)

@post('/uredi_uporabnika/<emso>') 
def uredi_uporabnika_post(emso):
    uporabnik = aliUporabnik()
    admin = aliAdmin()
    if admin is None:
        return
    organizator = aliOrganizator()
    ime = request.forms.ime
    priimek = request.forms.priimek
    email = request.forms.email
    uporabnisko_ime = request.forms.username
    geslo = request.forms.password
    conn.commit()
    if len(geslo) < 4:
        nastaviSporocilo('Geslo mora imeti vsaj 4 znake.')
        return
    cur = conn.cursor()
    uporabnik2 = None
    try:
        uporabnik2 = cur.execute(
            "SELECT * FROM uporabnik WHERE emso = %s;", (emso, ))
    except:
        uporabnik2 = None
    if uporabnik2 is not None:
        nastaviSporocilo('Ureditev ni možna')
        return
    try:
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM uporabnik WHERE uporabnisko_ime = %s', (uporabnisko_ime, ))
        uporabnik2 = cur.fetchone()
    except:
        uporabnik2 = None
    if uporabnik2 is not None:
        nastaviSporocilo('Uporabnisko ime že obstaja!')
        return
    zgostitev = hashGesla(geslo)
    cur.execute("UPDATE uporabnik SET ime = %s, priimek = %s, email = %s, uporabnisko_ime = %s, geslo = %s WHERE emso = %s;", (ime, priimek, email, uporabnisko_ime, zgostitev, emso))
    conn.commit()
    cur.execute(
            "SELECT * FROM uporabnik")
    uporabniki = cur.fetchall()
    return template('pregled_uporabnikov.html', uporabniki=uporabniki, admin = admin, uporabnik = uporabnik, organizator = organizator,uporabnik2 = uporabnik2)


@get('/odstrani_uporabnika/<emso>')
def odstrani_uporabnika(emso):
    organizator = aliOrganizator()
    uporabnik = aliUporabnik()
    admin = aliAdmin()
    if admin is None:
        return
    cur.execute("DELETE FROM uporabnik WHERE emso = %s;", (emso, ))
    conn.commit()
    cur.execute(
            "SELECT * FROM uporabnik")
    uporabniki = cur.fetchall()
    return template('pregled_uporabnikov.html', uporabniki=uporabniki, admin = admin, uporabnik = uporabnik, organizator = organizator)

############################################
### Urejanje organizatorjev
############################################
@get('/pregled_organizatorjev')  
def pregled_organizatorjev():
    organizator = aliOrganizator()
    uporabnik = aliUporabnik()
    admin = aliAdmin()
    if admin is None:
        return
    organizatorji = []
    try:
        cur.execute(
            "SELECT * FROM organizator_letov")
        organizatorji = cur.fetchall()
        return template('pregled_organizatorjev.html', organizatorji=organizatorji, uporabnik=uporabnik,admin = admin, organizator = organizator)
    except:
        return "Napaka!"
    


@get('/uredi_organizatorja/<emso>') 
def uredi_organizatorja(emso):
    uporabnik = aliUporabnik()
    admin = aliAdmin()
    organizator = aliOrganizator()
    if admin is None:
        return
    cur.execute("SELECT * FROM organizator_letov WHERE emso = %s;", (emso, ))
    organizator2 = cur.fetchall()[0]
    return template('uredi_organizatorja.html', organizator=organizator, uporabnik=uporabnik,admin = admin, organizator2 = organizator2)

@post('/uredi_organizatorja/<emso>') 
def uredi_organizatorja_post(emso):
    uporabnik = aliUporabnik()
    admin = aliAdmin()
    if admin is None:
        return
    organizator2 = aliOrganizator()

    ime = request.forms.ime
    priimek = request.forms.priimek
    uporabnisko_ime = request.forms.username
    geslo = request.forms.password
    conn.commit()
    if len(geslo) < 4:
        nastaviSporocilo('Geslo mora imeti vsaj 4 znake.')
        return
    cur = conn.cursor()
    organizator = None
    try:
        organizator = cur.execute(
            "SELECT * FROM organizator_letov WHERE emso = %s;", (emso, ))
    except:
        organizator = None
    if organizator is not None:
        nastaviSporocilo('Ureditev ni možna')
        return
    try:
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM organizator_letov WHERE uporabnisko_ime = %s', (uporabnisko_ime, ))
        organizator = cur.fetchone()
    except:
        organizator = None
    if organizator is not None:
        nastaviSporocilo('Uporabnisko ime že obstaja!')
        return
    zgostitev = hashGesla(geslo)
    cur.execute("UPDATE organizator_letov SET ime = %s, priimek = %s, uporabnisko_ime = %s, geslo = %s WHERE emso = %s;", (ime, priimek, uporabnisko_ime, zgostitev, emso))
    conn.commit()
    cur.execute(
            "SELECT * FROM organizator_letov")
    organizatorji = cur.fetchall()
    return template('pregled_organizatorjev.html', organizatorji=organizatorji, admin = admin, uporabnik = uporabnik, organizator = organizator2)


@get('/odstrani_organizatorja/<emso>')
def odstrani_organizatorja(emso):
    uporabnik = aliUporabnik()
    admin = aliAdmin()
    if admin is None:
        return
    organizator = aliOrganizator()
    cur.execute("DELETE FROM organizator_letov WHERE emso = %s;", (emso, ))
    conn.commit()
    cur.execute(
            "SELECT * FROM organizator_letov")
    organizatorji = cur.fetchall()
    return template('pregled_organizatorjev.html', organizatorji=organizatorji, admin = admin, uporabnik = uporabnik, organizator = organizator)

############################################
### Povezava z bazo
############################################


# povezemo se z bazo
conn = psycopg2.connect(database=auth_g.db, user=auth_g.user,
                        password=auth_g.password, host=auth_g.host, port=DB_PORT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# zazenemo/povezemo se s streznikom
run(host='localhost', port=SERVER_PORT, reloader=True)  
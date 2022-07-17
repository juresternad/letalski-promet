import psycopg2
import psycopg2.extensions
import psycopg2.extras
from regex import P
from bottleext import *
import os
import hashlib
import auth_g

# se znebimo problemov s šumniki
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

baza_datoteka = 'letalski_promet.db'
static_dir = "./static"

SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
ROOT = os.environ.get('BOTTLE_ROOT', '/')
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)


# odkomentiraj, če želiš sporočila o napakah
debug(True)

####################################################

# TODO popravi selecte tako da izberes le ustrezne stolpce in ne v oklepajih

@get('/')  # landing page
def index():
    uporabnik = aliUporabnik()
    organizator = aliOrganizator()
    leti = []
    try:
        cur.execute(
            "SELECT * FROM let WHERE CURRENT_DATE < datum_odhoda OR (CURRENT_DATE = datum_odhoda AND CURRENT_TIME < ura_odhoda) ORDER BY datum_odhoda, ura_odhoda LIMIT 10;")
        leti = cur.fetchall()
    except:
        return "Napaka!"
    return template('index.html', leti=leti, uporabnik=uporabnik, organizator=organizator)

@get("/views/images/<filepath:re:.*\.(jpg|png|gif|ico|svg)>")
def img(filepath):
    return static_file(filepath, root="views/images")

@route("/static/<filename:path>")
def static(filename):
    return static_file(filename, root=static_dir)
    
@get('/last_minute')  # landing page
def last_minute():
    uporabnik = aliUporabnik()
    organizator = aliOrganizator()
    leti = []
    try:
        cur.execute(
            "SELECT * FROM let WHERE  datum_odhoda < CURRENT_DATE + INTERVAL '3 day' ORDER BY datum_odhoda, ura_odhoda;")
        leti = cur.fetchall()
    except:
        return "Napaka!"
    return template('last_minute.html', leti=leti, uporabnik=uporabnik, organizator=organizator)

@get('/vroci')  # landing page
def vroci():
    uporabnik = aliUporabnik()
    organizator = aliOrganizator()
    leti = []
    try:
        cur.execute(
            "SELECT * FROM let WHERE CURRENT_DATE < datum_odhoda OR (CURRENT_DATE = datum_odhoda AND CURRENT_TIME < ura_odhoda) ORDER BY st_zasedenih_mest[1] DESC, datum_odhoda, ura_odhoda LIMIT 10;")
        leti = cur.fetchall()
    except:
        return "Napaka!"
    return template('vroci.html', leti=leti, uporabnik=uporabnik, organizator=organizator)


@get('/carterski')  # landing page
def carterski():
    uporabnik = aliUporabnik()
    organizator = aliOrganizator()
    leti = []
    try:
        cur.execute(
            "SELECT * FROM let WHERE CURRENT_DATE < datum_odhoda OR (CURRENT_DATE = datum_odhoda AND CURRENT_TIME < ura_odhoda) ORDER BY datum_odhoda, ura_odhoda;")
        leti = cur.fetchall()
    except:
        return "Napaka!"
    return template('carterski.html', leti=leti, uporabnik=uporabnik, organizator=organizator)


@post('/leti/')  # poizvedba za let
def let():
    iz = request.forms.iz
    do = request.forms.do
    datum_odhoda = request.forms.datum_odhoda
    datum_vrnitve = request.forms.datum_vrnitve
    cur.execute("SELECT * FROM let WHERE vzletno_letalisce = %s AND pristajalno_letalisce = %s AND datum_prihoda = %s AND datum_odhoda = %s;",
                (iz, do, datum_odhoda, datum_vrnitve))
    ustrezni_leti = cur.fetchall()
    if ustrezni_leti == []:
        return f'<h2>Ni ustreznih letov!</h2><a href="/d/{"-".join(iz.split())}/{"-".join(do.split())}/{datum_odhoda}/{datum_vrnitve}">prestopi</a>'
    else:
        return template('ustrezni_leti.html', ustrezni_leti=ustrezni_leti)



# TODO povratna? to lahko das na zacetno stran in ce ni leta nazaj pac ni povratne
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
      # ali sploh lahko en uporabnik kupi več kart
      try:  # TODO problem je stevilka_sedeza ker ne ves kdaj je letalo polno
        for _ in range(st_kart):
            cur.execute("insert into karta (razred, uporabnisko_ime, stevilka_leta) values (%s,%s,%s);", 
            (razred, username, id_leta))
            conn.commit()
        cur.execute("SELECT * FROM let WHERE stevilka_leta = %s;", (id_leta, ))
        # TODO if ni vec prostih mest
        kup_karta = cur.fetchone()
        iz, do, datum, ura, st_zas_mest, st_pro_mest = kup_karta[1], kup_karta[2], kup_karta[3], kup_karta[5], kup_karta[10], kup_karta[11]
        if razred == "economy":
            st_zas_mest[0] += st_kart
            st_pro_mest[0] -= st_kart
        elif razred == "business":
            st_zas_mest[1] += st_kart
            st_pro_mest[1] -= st_kart
        else:
            st_zas_mest[2] += st_kart
            st_pro_mest[2] -= st_kart
        
        print(st_zas_mest, st_pro_mest)
        cur.execute("UPDATE let SET st_zasedenih_mest = %s, st_prostih_mest = %s WHERE stevilka_leta = %s;", (st_zas_mest, st_pro_mest, id_leta, ))
        return template('uspesen_nakup.html', iz=iz, do=do, datum=datum, ura=ura, st_kart=st_kart)
      except:
        return "Žal nakup karte ni bil uspešen!"
    else:
        redirect(url('/prijava'))



############################################
### Registracija, prijava
############################################


skrivnost = "banana"

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
        redirect(url('/profil_uporabnika')) # redirect to page you came from


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
    if username is not None:
        cur.execute(
            "SELECT emso, ime, priimek, uporabnisko_ime FROM uporabnik WHERE uporabnisko_ime = %s;", (username, ))
        uporabnik = cur.fetchone()
        cur.execute(
            "SELECT * FROM karta WHERE uporabnisko_ime = %s LIMIT 10;", (username, ))
        kupljene_karte = cur.fetchall()
        leti = []
        # TODO mogoce je bolje ce naredi join in je tako samo ena poizvedba
        for karta in kupljene_karte:
            stevilka_leta = karta[4]
            cur.execute(
            "SELECT stevilka_leta, vzletno_letalisce, pristajalno_letalisce, datum_odhoda, ura_odhoda FROM let WHERE stevilka_leta = %s LIMIT 1;", (stevilka_leta, )) # order by datum_nakupa
            leti.append(cur.fetchone())
        return template('profil_uporabnika.html', uporabnik=uporabnik, leti=leti, napaka=napaka)
    else:
        redirect(url('/prijava'))

@get('/kupljene_karte')
def kupljene_karte():
    napaka = nastaviSporocilo()
    username = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    if username is not None:
        cur.execute(
            "SELECT emso, ime, priimek, uporabnisko_ime FROM uporabnik WHERE uporabnisko_ime = %s;", (username, ))
        uporabnik = cur.fetchone()
        cur.execute(
            "SELECT * FROM karta WHERE uporabnisko_ime = %s LIMIT 10;", (username, ))
        kupljene_karte = cur.fetchall()
        leti = []
        # TODO mogoce je bolje ce naredi join in je tako samo ena poizvedba
        for karta in kupljene_karte:
            stevilka_leta = karta[4]
            cur.execute(
            "SELECT stevilka_leta, vzletno_letalisce, pristajalno_letalisce, datum_odhoda, ura_odhoda FROM let WHERE stevilka_leta = %s LIMIT 1;", (stevilka_leta, )) # order by datum_nakupa
            leti.append(cur.fetchone())
        return template('kupljene_karte.html', uporabnik=uporabnik, leti=leti, napaka=napaka)
    else:
        redirect(url('/prijava'))

@get('/profil_organizatorja')
def profil_organizatorja():
    napaka = nastaviSporocilo()
    username = request.get_cookie("uporabnisko_ime", secret=skrivnost)
    cur.execute(
        "SELECT emso, ime, priimek, uporabnisko_ime FROM organizator_letov WHERE uporabnisko_ime = %s;", (username, ))
    organizator_letov = cur.fetchall()
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


############################################
### Dodajanje leta
############################################

@get('/dodaj_let')
def dodaj_let_get():
    organizator = aliOrganizator()
    uporabnik = aliUporabnik()
    napaka = nastaviSporocilo()
    return template('dodaj_let.html', napaka=napaka, organizator=organizator, uporabnik = uporabnik)

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
    zasedena = [prostae,prostab,prostaf]
    cur = conn.cursor()
    cur.execute("INSERT INTO let (vzletno_letalisce, pristajalno_letalisce, datum_odhoda, datum_prihoda, ura_odhoda, ura_prihoda, letalo_id, ekipa, cena, st_zasedenih_mest, st_prostih_mest) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (vzletno_letalisce, pristajalno_letalisce, datum_odhoda, datum_prihoda, ura_odhoda, ura_prihoda, letalo_id, ekipa, cena, zasedena, [0,0,0] ))
    conn.commit()
    redirect(url('/dodaj_let'))
####################################################

############################################
### Optimalna pot - Dijkstra
############################################
from dijkstra import slovar_letalisc, dijkstraish, pot
from datetime import datetime

@get('/d/<iz>/<do>/<datum_odhoda>/<datum_prihoda>')
def d(iz, do, datum_odhoda, datum_prihoda):
    try: 
        cur.execute('SELECT stevilka_leta, vzletno_letalisce, pristajalno_letalisce, datum_odhoda, datum_prihoda, ura_odhoda, ura_prihoda, cena FROM let WHERE datum_odhoda >= %s AND datum_odhoda <= %s;', (datum_odhoda, datum_prihoda))
        leti = cur.fetchall()
        # print(len(leti))
        G = [[] for _ in range(len(slovar_letalisc))] # seznam sosednosti
        for let in leti:
            # stevilka_leta = let[0]
            stevilka_leta, vzletno_letalisce, pristajalno_letalisce, datum_odhoda, datum_prihoda, ura_odhoda, ura_prihoda, cena = let
            if vzletno_letalisce not in slovar_letalisc:
                continue
            d1 = datetime.combine(datum_odhoda, ura_odhoda)
            t1 = datetime.timestamp(d1)
            d2 = datetime.combine(datum_prihoda, ura_prihoda)
            t2 = datetime.timestamp(d2)
            G[slovar_letalisc[vzletno_letalisce]].append((cena, t1, t2, slovar_letalisc[pristajalno_letalisce], stevilka_leta))
        # print(G)
        # print(len(G))
        s, t = slovar_letalisc[" ".join(iz.split("-"))], slovar_letalisc[" ".join(do.split("-"))]
        cena_potovanja, pot = dijkstraish(G, s, t)
        # print(cena_potovanja, pot)
        zaporedni_leti = []
        # TODO to je cisto prevec poizvedb ko delas s for zanko (ali se da narediti poizvedbo v enem kosu??)
        for st_leta in pot:
            cur.execute('SELECT vzletno_letalisce, pristajalno_letalisce, datum_odhoda, datum_prihoda, ura_odhoda, ura_prihoda, cena, stevilka_leta FROM let WHERE stevilka_leta = %s', (st_leta, ))
            zaporedni_leti.append(cur.fetchone())
        return template('dijkstra_let.html', cena_potovanja=cena_potovanja, zaporedni_leti=zaporedni_leti)
    except:
        return "nista"





###################################################
@get('/org')  # landing page
def org():
    uporabnik = aliUporabnik()
    organizator = aliOrganizator()
    leti = []
    try:
        cur.execute(
            "SELECT * FROM let")
        leti = cur.fetchall()
    except:
        return "Napaka!"
    return template('org.html', leti=leti, uporabnik=uporabnik, organizator=organizator)



@get('/uredi/<id_leta>')
def uredi(id_leta):
    try:
        cur.execute("SELECT * FROM let WHERE stevilka_leta = %s;", (id_leta, ))
        let = cur.fetchall()[0]
        return template('uredi.html', let=let)
    except:
        return "Izbrani let ni na voljo!"

@post('/uredi/<id_leta>') 
def uredi_let(id_leta):
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
    zasedena = [prostae,prostab,prostaf]
    cur.execute("UPDATE let SET vzletno_letalisce = %s, pristajalno_letalisce = %s, datum_odhoda = %s, datum_prihoda = %s, ura_odhoda = %s, ura_prihoda = %s, letalo_id = %s, ekipa = %s, cena = %s, st_zasedenih_mest = %s, st_prostih_mest = %s WHERE stevilka_leta = %s;", (vzletno_letalisce, pristajalno_letalisce, datum_odhoda, datum_prihoda, ura_odhoda, ura_prihoda, letalo_id, ekipa, cena, [0,0,0], zasedena,  id_leta ))
    conn.commit()
    return template('org.html', let=let)


@get('/odstrani/<id_leta>')
def odstrani(id_leta):
    try:
        cur.execute("DELETE FROM let WHERE stevilka_leta = %s;", (id_leta, ))
        conn.commit()
        return template('org.html', let=let)
    except:
        return "Izbrani let ni na voljo!"






















# povezemo se z bazo
conn = psycopg2.connect(database=auth_g.db, user=auth_g.user,
                        password=auth_g.password, host=auth_g.host, port=DB_PORT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# zazenemo/povezemo se s streznikom
run(host='localhost', port=SERVER_PORT, reloader=True)
import psycopg2, psycopg2.extensions, psycopg2.extras
from bottle import *
import auth
import os
import hashlib

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

# odkomentiraj, če želiš sporočila o napakah TODO
debug(True)

####################################################
@get('/') # landing page
def index():
    cur.execute("SELECT (vzletno_letalisce, pristajalno_letalisce, cas_odhoda, cas_prihoda) FROM let;")
    leti = cur.fetchall()
    # grdo sej vem :()
    print(leti[0][0].split(','))
    nleti = []
    for let in leti:
        let = let[0].split(',')
        vzletno = let[0][2:-1]
        pristajalno = let[1][1:-1]
        cas_odhoda = let[2]
        cas_prihoda = let[3][:-1]
        nleti.append([vzletno, pristajalno, cas_odhoda, cas_prihoda])
    return template('index.html', leti=nleti)

@post('/leti/') # poizvedba za let
def let():
    iz = request.forms.iz
    do = request.forms.do
    datum_odhoda = request.forms.datum_odhoda
    datum_vrnitve = request.forms.datum_vrnitve
    cur.execute("SELECT * FROM let WHERE vzletno_letalisce = %s AND pristajalno_letalisce = %s AND cas_prihoda = %s AND cas_odhoda = %s", (iz, do, datum_odhoda, datum_vrnitve))
    ustrezni_leti = cur.fetchall()
    if ustrezni_leti == []:
        return '<h2>Ni ustreznih letov!</h2>'
    else:
        return template('ustrezni_leti.html', ustrezni_leti=ustrezni_leti)

@get('/prijava') 
def prijava():
    return template('prijava.html')

@get('/registracija') 
def registracija():
    return template('registracija.html')

# @get('/kupi/<id_leta>/')
# def kupi_karto(id_leta, st_kart=1):
#     cur.execute("insert into karta (st_narocila, razred, ime_potnika, cena, stevilka_sedeza, stevilka_leta) values (9,150, 'Boeing 767', 0);")
#     return f"uspešno ste kupili karto za let {id_leta}"

# TODO
############################################
### Registracija, prijava
############################################
def nastaviSporocilo(sporocilo = None):
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
    telefon = request.forms.telefon
    datum_rojstva = request.forms.datum_rojstva
    uporabnisko_ime = request.forms.uporabnisko_ime
    geslo = request.forms.geslo
    geslo2 = request.forms.geslo2
    if emso is None or uporabnisko_ime is None or geslo is None or geslo2 is None:
        nastaviSporocilo('Registracija ni možna') 
        redirect('/registracija')
        return
    # cur = baza.cursor()    
    uporabnik = None
    try: 
        uporabnik = cur.execute("SELECT * FROM uporabnik WHERE emso = ?", (emso, )).fetchone()
    except:
        uporabnik = None
    if uporabnik is None:
        nastaviSporocilo('Registracija ni možna') 
        redirect('/registracija')
        return
    if len(geslo) < 4:
        nastaviSporocilo('Geslo mora imeti vsaj 4 znake.') 
        redirect('/registracija')
        return
    if geslo != geslo2:
        nastaviSporocilo('Gesli se ne ujemata.') 
        redirect('/registracija')
        return
    zgostitev = hashGesla(geslo)
    cur.execute("UPDATE uporabnik SET uporabnisko_ime = ?, geslo = ? WHERE emso = ?", (uporabnisko_ime, zgostitev, emso))
    response.set_cookie('uporabnisko_ime', uporabnisko_ime, secret=skrivnost)
    redirect('/')


@get('/prijava')
def prijava_get():
    napaka = nastaviSporocilo()
    return template('prijava.html', napaka=napaka)

@post('/prijava')
def prijava_post():
    uporabnisko_ime = request.forms.uporabnisko_ime
    geslo = request.forms.geslo
    if uporabnisko_ime is None or geslo is None:
        nastaviSporocilo('Uporabniško ima in geslo morata biti neprazna') 
        redirect('/prijava')
        return
    # cur = baza.cursor()    
    hashBaza = None
    try: 
        hashBaza = cur.execute("SELECT geslo FROM uporabnik WHERE uporabnisko_ime = ?", (uporabnisko_ime, )).fetchone()
        hashBaza = hashBaza[0]
    except:
        hashBaza = None
    if hashBaza is None:
        nastaviSporocilo('Uporabniško geslo ali ime nista ustrezni') 
        redirect('/prijava')
        return
    if hashGesla(geslo) != hashBaza:
        nastaviSporocilo('Uporabniško geslo ali ime nista ustrezni') 
        redirect('/prijava')
        return
    response.set_cookie('uporabnisko_ime', uporabnisko_ime, secret=skrivnost)
    redirect('/')
    
@get('/odjava')
def odjava_get():
    response.delete_cookie('uporabnisko_ime')
    redirect('/prijava')


####################################################

# povezemo se z bazo
conn = psycopg2.connect(database=auth.db, user=auth.user, password=auth.password, host=auth.host, port=DB_PORT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# zazenemo/povezemo se s streznikom
if __name__ == '__main__':
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
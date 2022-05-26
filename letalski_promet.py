import psycopg2, psycopg2.extensions, psycopg2.extras
from bottle import *
import auth
import os

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
    return template('index.html', leti=leti)

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


####################################################

# povezemo se z bazo
conn = psycopg2.connect(database=auth.db, user=auth.user, password=auth.password, host=auth.host, port=DB_PORT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# zazenemo/povezemo se s streznikom
if __name__ == '__main__':
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
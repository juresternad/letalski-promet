import psycopg2, psycopg2.extensions, psycopg2.extras
from bottle import route, run, abort, get, post, debug, template
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
    cur.execute("SELECT (vzletno_letalisce, pristajalno_letalisce, cas_odhoda, cas_prihoda) FROM let")
    leti = cur.fetchall()
    # TODO
    # naredi form za vnos podatkov
    # lepo izpisi po alinejah
    print(leti[0])
    return template('index.html', leti=leti)

@get('leti/<povratna>/<iz>/<do>/<datum_odhoda>/<datum_vrnitve>/<st_kart>/') # poizvedba za let
def let(povratna, iz, do, datum_odhoda, datum_vrnitve, st_kart="1"):
    cur.execute("SELECT * FROM let WHERE od = %s AND do = %s AND datum_odhoda = %s AND datum_vrnitve = %s", (od, do, datum_odhoda, datum_vrnitve))
    return "blah"

@post('/let/<id_leta>/st_kart/<st_kart>/')
def kupi_karto(id_leta, st_kart):
    pass

####################################################

# povezemo se z bazo
conn = psycopg2.connect(database=auth.db, user=auth.user, password=auth.password, host=auth.host, port=DB_PORT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# zazenemo/povezemo se s streznikom
if __name__ == '__main__':
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
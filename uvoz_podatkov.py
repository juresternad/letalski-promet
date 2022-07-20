import psycopg2, psycopg2.extensions, psycopg2.extras 
from psycopg2 import sql
import csv
from auth_public import *
from auth_g import *

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)



conn = psycopg2.connect(database=db,
                        host=host,
                        user=user,
                        password=password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 



def importSQL(file):
    with open(file) as f:
        s = f.read()
        cur.execute(s)
    conn.commit()


importSQL('letalski_promet.sql')
importSQL('podatki/druzbe.sql')
importSQL('podatki/letalo.sql')
importSQL('podatki/let.sql')
importSQL('podatki/delavci_na_letu.sql')
importSQL('podatki/uporabnik.sql')


# zniža cene last minute letov
cur.execute(
        "SELECT cena, stevilka_leta FROM let WHERE  datum_odhoda < CURRENT_DATE + INTERVAL '3 day' ORDER BY datum_odhoda, ura_odhoda;")
leti = cur.fetchall()
for let in leti:
    cena, stevilka_leta = let
    print(cena)
    for i in range(2):
        cena[i]= round(int(cena[i])*0.5,1)
    cur.execute("UPDATE let SET cena = %s WHERE stevilka_leta = %s", (cena ,stevilka_leta))
    conn.commit()
    leti.remove(let)

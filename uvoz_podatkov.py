import psycopg2, psycopg2.extensions, psycopg2.extras 
from psycopg2 import sql
import csv
# from auth_public import *
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



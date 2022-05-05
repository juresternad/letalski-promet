import psycopg2, psycopg2.extensions, psycopg2.extras 
from psycopg2 import sql
import csv
from auth_public import *
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
importSQL('podatki\delavci_na_letu.sql')
importSQL('podatki\let.sql')
importSQL('podatki\letalo.sql')
importSQL('podatki\druzbe.sql')



def importCSV(table):
    with open('podatki/{0}.csv'.format(table)) as csvfile:
        data = csv.reader(csvfile)   
        rows = [row for row in data]
        head = rows[0]
        body = rows[1:]
        cur.executemany("INSERT INTO {0} ({1}) VALUES ({2})".format(
            table, ",".join(head), ",".join(['?']*len(head))), body)
    conn.commit()
    

importCSV('letalski_promet.sql')
importCSV('podatki\delavci_na_letu.sql')
importCSV('podatki\let.sql')
importCSV('podatki\letalo.sql')
importCSV('podatki\druzbe.sql')
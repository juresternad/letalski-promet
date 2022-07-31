import psycopg2, psycopg2.extensions, psycopg2.extras 
from psycopg2 import sql
import csv
from auth_public import *
from auth_g import *
import datetime
from datetime import date
from datetime import timedelta



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
importSQL('podatki/delavci_na_letu.sql')
importSQL('podatki/uporabnik.sql')


leti_sez = [
('Madrid Barajas Airport (MAD)', 'Barcelona Airport (BCN)', '2022-07-21', '2022-07-21', '06:00:00', '07:00:00', 4,4, [30,60,120],'{0,0,0}','{290,29,58}'),
('Rome Fiumicino Airport (FCO)', 'Zurich Airport (ZRH)', '2022-07-21', '2022-07-21', '06:00:00', '08:00:00', 3,3, [40,80,160],'{0,0,0}','{190,19,38}'),
('Athens Airport (ATH)', 'Munich International Airport (MUC)', '2022-07-21', '2022-07-21', '06:00:00', '10:00:00', 8,8, [50,100,200],'{0,0,0}','{140,14,28}'),
('Amsterdam Airport (AMS)', 'Frankfurt International Airport (FRA)', '2022-07-21', '2022-07-21', '06:00:00', '07:00:00', 2,2, [20,40,80],'{0,0,0}','{150,15,30}'),
('London Heathrow Airport (LHR)', 'Paris Charles de Gaulle Airport (CDG)', '2022-07-21', '2022-07-21', '06:00:00', '08:00:00', 0,0, [25,50,75],'{0,0,0}','{190,19,38}'),

('Barcelona Airport (BCN)', 'Zurich Airport (ZRH)', '2022-07-21', '2022-07-21', '08:00:00', '09:00:00', 6,6,[45,90,180],'{0,0,0}','{300,30,60}'),
('Zurich Airport (ZRH)', 'Munich International Airport (MUC)', '2022-07-21', '2022-07-21', '10:00:00', '11:00:00', 9,9, [40,80,160],'{0,0,0}','{150,15,30}'),
('Munich International Airport (MUC)', 'Frankfurt International Airport (FRA)', '2022-07-21', '2022-07-21', '12:00:00', '13:00:00', 5,5, [20,40,80],'{0,0,0}','{100,10,20}'),
('Frankfurt International Airport (FRA)', 'Paris Charles de Gaulle Airport (CDG)', '2022-07-21', '2022-07-21', '14:00:00', '15:00:00', 7,7, [30,60,120],'{0,0,0}','{150,15,30}'),
('Paris Charles de Gaulle Airport (CDG)', 'Barcelona Airport (BCN)', '2022-07-21', '2022-07-21', '16:00:00', '18:00:00', 1,1, [45,90,180],'{0,0,0}','{220,22,44}'),


('Barcelona Airport (BCN)', 'Madrid Barajas Airport (MAD)', '2022-07-21', '2022-07-21', '19:00:00', '20:00:00', 4,4, [30,60,120],'{0,0,0}','{290,29,58}'),
('Zurich Airport (ZRH)', 'Rome Fiumicino Airport (FCO)', '2022-07-21', '2022-07-21', '19:00:00', '21:00:00', 3,3, [40,80,160],'{0,0,0}','{190,19,38}'),
('Munich International Airport (MUC)', 'Athens Airport (ATH)', '2022-07-21', '2022-07-21', '19:00:00', '23:00:00', 8,8, [50,100,20],'{0,0,0}','{140,14,28}'),
('Frankfurt International Airport (FRA)', 'Amsterdam Airport (AMS)', '2022-07-21', '2022-07-21', '19:00:00', '20:00:00', 2,2, [20,40,80],'{0,0,0}','{150,15,30}'),
('Paris Charles de Gaulle Airport (CDG)', 'London Heathrow Airport (LHR)', '2022-07-21', '2022-07-21', '19:00:00', '22:00:00', 0,0, [25,50,75],'{0,0,0}','{190,19,38}'),

('Zurich Airport (ZRH)', 'Barcelona Airport (BCN)', '2022-07-21', '2022-07-21', '15:00:00', '16:00:00', 6,6, [45,90,180],'{0,0,0}','{300,30,60}'),
('Munich International Airport (MUC)', 'Zurich Airport (ZRH)', '2022-07-21', '2022-07-21', '17:00:00', '18:00:00', 9,9, [40,80,160],'{0,0,0}','{150,15,30}'),
('Frankfurt International Airport (FRA)', 'Munich International Airport (MUC)', '2022-07-21', '2022-07-21', '19:00:00', '20:00:00', 5,5, [20,40,80],'{0,0,0}','{100,10,20}'),
('Paris Charles de Gaulle Airport (CDG)', 'Frankfurt International Airport (FRA)', '2022-07-21', '2022-07-21', '21:00:00', '22:00:00', 7,7, [30,60,120],'{0,0,0}','{150,15,30}'),
('Barcelona Airport (BCN)', 'Paris Charles de Gaulle Airport (CDG)', '2022-07-21', '2022-07-21', '21:00:00', '23:00:00', 1,1, [45,90,180],'{0,0,0}','{220,22,44}')
]

for let in leti_sez:
    day = date.today()
    cena= let[8]
    print(cena)
    for j in range(4,20):
        day_add = day + timedelta(days=j)
        cur.execute("INSERT INTO let (vzletno_letalisce, pristajalno_letalisce, datum_odhoda, datum_prihoda, ura_odhoda, ura_prihoda, letalo_id, ekipa, cena, st_zasedenih_mest, st_prostih_mest) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (let[0],let[1],day_add,day_add,let[4],let[5],let[6],let[7],cena,let[9],let[10]))
        conn.commit()
    for i in range(2):
        cena[i]= round(int(cena[i])*0.5,1)
    for j in range(3):
        day_add = day + timedelta(days=j)
        cur.execute("INSERT INTO let (vzletno_letalisce, pristajalno_letalisce, datum_odhoda, datum_prihoda, ura_odhoda, ura_prihoda, letalo_id, ekipa, cena, st_zasedenih_mest, st_prostih_mest) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (let[0],let[1],day_add,day_add,let[4],let[5],let[6],let[7],cena,let[9],let[10]))
        conn.commit()
    


# zniža cene last minute letov
# cur.execute(
#         "SELECT cena, stevilka_leta FROM let WHERE  datum_odhoda < CURRENT_DATE + INTERVAL '3 day' ORDER BY datum_odhoda, ura_odhoda;")
# leti = cur.fetchall()
# for let in leti:
#     cena, stevilka_leta = let
#     print(cena)
#     for i in range(2):
#         cena[i]= round(int(cena[i])*0.5,1)
#     cur.execute("UPDATE let SET cena = %s WHERE stevilka_leta = %s", (cena ,stevilka_leta))
#     conn.commit()
#     leti.remove(let)

  
# taking input as the current date
# today() method is supported by date 
# class in datetime module


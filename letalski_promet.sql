
DROP TABLE IF EXISTS delavec_na_letu CASCADE;
DROP TABLE IF EXISTS druzba CASCADE;
DROP TABLE IF EXISTS karta CASCADE;
DROP TABLE IF EXISTS let CASCADE;
DROP TABLE IF EXISTS letalo CASCADE;
DROP TABLE IF EXISTS uporabnik CASCADE;
DROP TABLE IF EXISTS organizator_letov CASCADE;



CREATE TABLE druzba (
    id INTEGER PRIMARY KEY,
    ime_druzbe TEXT
);

CREATE TABLE letalo (
    id INTEGER PRIMARY KEY,
    stevilo_sedezev INTEGER[3],
    model TEXT NOT NULL,
    druzba INTEGER NOT NULL REFERENCES druzba(id)
);

CREATE TABLE let (
    stevilka_leta SERIAL PRIMARY KEY,
    vzletno_letalisce TEXT NOT NULL,
    pristajalno_letalisce TEXT NOT NULL,
    datum_odhoda DATE NOT NULL,
    datum_prihoda DATE NOT NULL,
    ura_odhoda TIME NOT NULL,
    ura_prihoda TIME NOT NULL,
    letalo_id INTEGER NOT NULL REFERENCES letalo(id),
    ekipa INTEGER NOT NULL,
    cena INTEGER[3],
    st_zasedenih_mest INTEGER[3],
    st_prostih_mest INTEGER[3]
);

CREATE TABLE delavec_na_letu (
    id INTEGER PRIMARY KEY,
    ime TEXT NOT NULL,
    delo TEXT NOT NULL,
    starost INTEGER NOT NULL,
    ekipa INTEGER NOT NULL
);

CREATE TABLE uporabnik (
    emso INTEGER PRIMARY KEY,
    ime TEXT NOT NULL,
    priimek TEXT NOT NULL,
    email TEXT NOT NULL,
    uporabnisko_ime TEXT UNIQUE NOT NULL,
    geslo TEXT NOT NULL
);

CREATE TABLE karta (
    stevilka_narocila SERIAL PRIMARY KEY,
    razred TEXT NOT NULL,
    uporabnisko_ime TEXT REFERENCES uporabnik(uporabnisko_ime) ON DELETE CASCADE,
    stevilka_sedeza SERIAL,
    stevilka_leta INTEGER NOT NULL REFERENCES let(stevilka_leta) ON DELETE CASCADE
);



CREATE TABLE organizator_letov (
    emso INTEGER PRIMARY KEY,
    ime TEXT NOT NULL,
    priimek TEXT NOT NULL,
    uporabnisko_ime TEXT UNIQUE NOT NULL,
    geslo TEXT NOT NULL 
);

-- dodelimo pravice 
GRANT ALL ON DATABASE sem2022_gasperk TO gasperk;
GRANT ALL ON SCHEMA public TO gasperk;
GRANT ALL ON ALL TABLES IN SCHEMA public TO gasperk;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO gasperk;


GRANT ALL ON DATABASE sem2022_gasperk TO jurest;
GRANT ALL ON SCHEMA public TO jurest;
GRANT ALL ON ALL TABLES IN SCHEMA public TO jurest;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO jurest;

GRANT ALL ON DATABASE sem2022_gasperk TO javnost;
GRANT ALL ON SCHEMA public TO javnost;
GRANT ALL ON ALL TABLES IN SCHEMA public TO javnost;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO javnost;


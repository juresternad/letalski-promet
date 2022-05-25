
DROP TABLE IF EXISTS delavec_na_letu CASCADE;
DROP TABLE IF EXISTS druzba CASCADE;
DROP TABLE IF EXISTS karta CASCADE;
DROP TABLE IF EXISTS let CASCADE;
DROP TABLE IF EXISTS letalo CASCADE;


CREATE TABLE druzba (
    id INTEGER PRIMARY KEY,
    ime_druzbe TEXT
);

CREATE TABLE letalo (
    id INTEGER PRIMARY KEY,
    stevilo_sedezev INTEGER NOT NULL,
    model TEXT NOT NULL,
    druzba INTEGER NOT NULL REFERENCES druzba(id)
);

CREATE TABLE let (
    stevilka_leta INTEGER PRIMARY KEY,
    vzletno_letalisce TEXT NOT NULL,
    pristajalno_letalisce TEXT NOT NULL,
    cas_prihoda DATE NOT NULL,
    cas_odhoda DATE NOT NULL,
    letalo_id INTEGER NOT NULL REFERENCES letalo(id),
    ekipa INTEGER NOT NULL
);


CREATE TABLE delavec_na_letu (
    id INTEGER PRIMARY KEY,
    ime TEXT NOT NULL,
    delo TEXT NOT NULL,
    starost INTEGER NOT NULL,
    ekipa INTEGER NOT NULL
);



CREATE TABLE karta (
    stevilka_narocila INTEGER PRIMARY KEY,
    razred TEXT NOT NULL,
    ime_potnika TEXT NOT NULL,
    cena INTEGER NOT NULL,
    stevilka_sedeza TEXT NOT NULL,
    stevilka_leta INTEGER NOT NULL REFERENCES let(stevilka_leta)
);

CREATE TABLE uporabnik (
    emso INTEGER PRIMARY KEY,
    ime TEXT NOT NULL,
    priimek TEXT NOT NULL,
    uporabnisko_ime TEXT UNIQUE NOT NULL,
    geslo TEXT NOT NULL, -- ali je taprav type
    email TEXT NOT NULL, -- type?
    telefon TEXT NOT NULL, -- type?
    datum_rojstva DATE NOT NULL,
    spol TEXT NOT NULL,
    drzava TEXT NOT NULL,
    kraj TEXT NOT NULL,
    naslov TEXT NOT NULL,
    posta TEXT NOT NULL,
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


GRANT ALL ON DATABASE sem2022_gasperk TO filipb;
GRANT ALL ON SCHEMA public TO filipb;
GRANT ALL ON ALL TABLES IN SCHEMA public TO filipb;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO filipb;

--  dodatne pravice za uporabo aplikacije
--  GRANT INSERT ON karta TO potniki;
--  GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO javnost;



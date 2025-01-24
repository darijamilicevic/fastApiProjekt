from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import redis
import json

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "lozinka")
DB_NAME = os.environ.get("DB_NAME", "todo_baza")

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
redisKes = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True) 

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="frontend")

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

zadaci_tagovi = Table(
    "zadaci_tagovi",
    Base.metadata,
    Column("zadatak_id", Integer, ForeignKey("zadaci.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
)

class Zadatak(Base):
    __tablename__ = "zadaci"
    id = Column(Integer, primary_key=True, index=True)
    naslov = Column(String(100), nullable=False)
    obavljeno = Column(Boolean, default=False)
    

    kategorija_id = Column(Integer, ForeignKey("kategorija.id"))
    korisnik_id = Column(Integer, ForeignKey("korisnik.id"))

    kategorija = relationship("Kategorija", back_populates="zadaci")
    korisnik = relationship("Korisnik", back_populates="zadaci")
    tagovi = relationship("Tag", secondary=zadaci_tagovi, back_populates="zadaci")
    komentari = relationship("Komentar", back_populates="zadatak")

class Kategorija(Base):
    __tablename__ = "kategorija"
    id = Column(Integer, primary_key=True, index=True)
    naziv = Column(String(50), nullable=False)

    zadaci = relationship("Zadatak", back_populates="kategorija")

class Korisnik(Base):
    __tablename__ = "korisnik"
    id = Column(Integer, primary_key=True, index=True)
    ime = Column(String(50), nullable=False)
    prezime = Column(String(50), nullable=False)

    zadaci = relationship("Zadatak", back_populates="korisnik")

class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, index=True)
    naziv = Column(String(50), nullable=False)

    zadaci = relationship("Zadatak", secondary=zadaci_tagovi, back_populates="tagovi")

class Komentar(Base):
    __tablename__ = "komentar"
    id = Column(Integer, primary_key=True, index=True)
    sadrzaj = Column(String(255), nullable=False)

    zadatak_id = Column(Integer, ForeignKey("zadaci.id"))
    zadatak = relationship("Zadatak", back_populates="komentari")

@app.on_event("startup")
def inicijaliziraj_bazu():
    Base.metadata.create_all(bind=engine)

def dobavi_bazu():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def prikazi_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/kategorije")
def sve_kategorije(db=Depends(dobavi_bazu)):
    return db.query(Kategorija).all()

@app.get("/api/korisnici")
def svi_korisnici(db=Depends(dobavi_bazu)):
    return db.query(Korisnik).all()

@app.get("/api/tagovi")
def svi_tagovi(db=Depends(dobavi_bazu)):
    return db.query(Tag).all()

class ZadatakKompletanUnos(BaseModel):
    naslov: str
    kategorija_id: int
    korisnik_id: int
    tag_ids: List[int] = []
    komentar: Optional[str] = None

@app.post("/api/zadaci_komplet")
def kreiraj_zadatak_komplet(podaci: ZadatakKompletanUnos, db=Depends(dobavi_bazu)):
    novi_zad = Zadatak(
        naslov=podaci.naslov,
        kategorija_id=podaci.kategorija_id,
        korisnik_id=podaci.korisnik_id
    )
    db.add(novi_zad)
    db.commit()
    db.refresh(novi_zad)

    for tag_id in podaci.tag_ids:
        tag_obj = db.query(Tag).get(tag_id)
        if tag_obj:
            novi_zad.tagovi.append(tag_obj)

    if podaci.komentar:
        novi_kom = Komentar(sadrzaj=podaci.komentar, zadatak_id=novi_zad.id)
        db.add(novi_kom)

    db.commit()
    db.refresh(novi_zad)

    redisKes.delete("svi_zadaci")  #izbrisi kes

    return {
        "id": novi_zad.id,
        "naslov": novi_zad.naslov,
        "kategorija_id": novi_zad.kategorija_id,
        "korisnik_id": novi_zad.korisnik_id,
        "tag_ids": [t.id for t in novi_zad.tagovi],
        "komentari": [k.sadrzaj for k in novi_zad.komentari]
    }

@app.get("/api/zadaci")
def svi_zadaci(db=Depends(dobavi_bazu)):

    cache_key = "svi_zadaci"
    data = redisKes.get(cache_key) # dohvati kes
    if data:
        return json.loads(data)
    zadaci_db = db.query(Zadatak).all()
    output = []
    for z in zadaci_db:
        output.append({
            "id": z.id,
            "naslov": z.naslov,
            "kategorija": z.kategorija.naziv if z.kategorija else None,
            "korisnik": f"{z.korisnik.ime} {z.korisnik.prezime}" if z.korisnik else None,
            "tagovi": [tag.naziv for tag in z.tagovi],
            "komentari": [kom.sadrzaj for kom in z.komentari]
        })
    redisKes.set(cache_key, json.dumps(output)) #dodaj kes
    return output
